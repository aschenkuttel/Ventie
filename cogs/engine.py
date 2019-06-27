from config import database, db_key, db_user, host
from family import Queue, Session, Anon
from discord.ext import commands, tasks
import asyncpg
import utils


class Engine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None
        self.queue = None
        self.sessions = {}
        self.cardinal.start()

    async def cog_check(self, ctx):
        if ctx.guild:
            raise commands.PrivateMessageOnly
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setup()
        print("Ready to Vent!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild:
            return
        session = self.get_session(message.author.id)
        if session is None:
            return
        user_id, nick = session.get_partner(message.author.id)
        user = self.bot.get_user(user_id)
        if not user:
            return await self.lost_user(session, user_id)
        msg = f"**{nick}:** {message.content}"
        await user.send(msg)

    @tasks.loop(seconds=3.0)
    async def cardinal(self):
        if self.pool is None:
            return
        result = self.queue.get_pair()
        if not result:
            return
        try:
            session = Session(self.pool, *result)
            self.sessions[session.id] = session
            await self.introduction(result)
        except Exception as e:
            print(e)

    @cardinal.before_loop
    async def before_cardinal(self):
        await self.bot.wait_until_ready()

    async def setup(self):
        conn_data = {"host": host, "port": "5432", "user": db_user,
                     "password": db_key, "database": database, "loop": self.bot.loop}
        self.pool = await asyncpg.create_pool(**conn_data)
        self.bot.pool = self.pool
        await self.load_cache()
        self.queue = Queue()

    async def load_cache(self):
        conn = await self.pool.acquire()
        query = "SELECT * FROM session"
        data = await conn.fetch(query)
        await self.pool.release(conn)
        for record in data:
            session = Session.from_record(self.pool, record)
            self.sessions[session.id] = session

    def get_session(self, user_id):
        for session in self.sessions:
            if user_id in session:
                return session

    async def introduction(self, pair):
        for user in pair:
            embed = utils.embed_intro(pair)
            await user.send(embed=embed)

    async def lost_user(self, session, lost_id):
        other_id = session.get_partner(lost_id)
        user = self.bot.get_user(other_id)
        if not user:
            pass
        else:
            msg = "empty"
            await user.send(utils.embed_leave(msg))
        await session.finish()

    @commands.command(name="vent", aliases=["listen"])
    async def vent_(self, ctx, alias=None):

        if self.get_session(ctx.author.id):
            raise utils.ActiveSession

        status = ctx.invoked_with == "vent"
        alias = alias if alias else utils.random_nick()

        user = Anon(ctx.author, alias)
        self.queue.add_user(user, status)
        title = "Successfully added to queue!"
        msg = f"**Nickname:** `{alias}`"
        await ctx.author.send(embed=utils.embed_confirm(msg, title, self.queue.status))

    @commands.command(name="leave")
    async def leave_(self, ctx):

        session = self.get_session(ctx.author.id)
        if session is None:
            raise utils.NoSession

        user_id, own_nick = session.get_partner(ctx.author.id)
        user = self.bot.get_user(user_id)

        msg = f"`{own_nick}` left the chat..."
        await user.send(embed=utils.embed_leave(msg))


def setup(bot):
    bot.add_cog(Engine(bot))
