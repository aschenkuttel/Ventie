from config import database, db_key, db_user, host
from family import Queue, Session, Anon
from discord.ext import commands, tasks
import datetime
import asyncpg
import discord
import utils


class Engine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None
        self.queue = None
        self.sessions = {}
        self.judge.start()
        self.cardinal.start()
        self.bot.add_check(self.global_check)
        self.judge.add_exception_type(asyncpg.PostgresConnectionError)

    async def cog_check(self, ctx):
        if ctx.guild:
            raise commands.PrivateMessageOnly()
        return True

    async def global_check(self, ctx):
        conn = await self.pool.acquire()
        query = "SELECT * FROM blacklist WHERE id = $1"
        banned = await conn.fetchrow(query, ctx.author.id)
        await self.pool.release(conn)
        if banned is None:
            return True
        date = datetime.datetime.now()
        still = (banned['till'] - date).days
        raise utils.StillBanned(still)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setup()
        print("Ready to Vent!")

    # Main Listener / Router
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild:
            return
        if message.content.startswith("."):
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

    # Main Loop
    @tasks.loop(seconds=3.0)
    async def cardinal(self):
        if self.pool is None:
            return
        result = self.queue.get_pair()
        if not result:
            return
        session = Session(self.pool, *result)
        await session.setup()
        self.sessions[session.id] = session
        await self.introduction(result)

    @tasks.loop(hours=12)
    async def judge(self):
        if self.pool is None:
            return
        conn = await self.pool.acquire()
        query = "SELECT * FROM blacklist"
        data = await conn.fetch(query)
        date = datetime.datetime.now()
        for record in data:
            if record['till'] < date:
                query = "DELETE FROM blacklist WHERE id = $1"
                await conn.execute(query, record['id'])
        await self.pool.release(conn)

    @cardinal.before_loop
    async def before_cardinal(self):
        await self.bot.wait_until_ready()

    @judge.before_loop
    async def before_cardinal(self):
        await self.bot.wait_until_ready()

    # DB / Cache Setup
    async def setup(self):
        conn_data = {"host": host, "port": "5432", "user": db_user,
                     "password": db_key, "database": database, "loop": self.bot.loop}
        self.pool = await asyncpg.create_pool(**conn_data)

        for name in self.bot.cogs:
            cog = self.bot.get_cog(name)
            cog.pool = self.pool

        await self.load_cache()
        if self.queue is None:
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
        for session in self.sessions.values():
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
            msg = "something went wrong, session over"
            await user.send(utils.embed_error(msg))
        await session.finish()

    @commands.command(name="vent", aliases=["listen"])
    async def vent_(self, ctx, alias=None):
        session = self.get_session(ctx.author.id)
        if session:
            raise utils.ActiveSession()

        if ctx.author.id in self.queue:
            raise utils.AlreadyQueued()

        status = ctx.invoked_with == "vent"
        alias = alias if alias else utils.random_nick()

        user = Anon(ctx.author, alias)
        self.queue.add_user(user, status)
        title = "Successfully added to queue!"
        msg = f"**Nickname:** {alias}"
        await ctx.author.send(embed=utils.embed_confirm(msg, title, self.queue.status))

    @commands.command(name="leave")
    async def leave_(self, ctx):
        if ctx.author.id in self.queue:
            self.queue.remove_user(ctx.author)
            msg = "you left the queue"
            return await ctx.send(embed=utils.embed_confirm(msg))

        session = self.get_session(ctx.author.id)
        if session is None:
            raise utils.NoSession()

        user_id, own_nick = session.get_partner(ctx.author.id)
        user = self.bot.get_user(user_id)

        msg = f"**{own_nick}** left the chat..."
        await user.send(embed=utils.embed_error(msg))
        await session.finish()
        del self.sessions[session.id]
        msg = "you left the session"
        await ctx.send(embed=utils.embed_confirm(msg))

    @commands.command(name="report")
    async def report_(self, ctx, *, reason: str):
        session = self.get_session(ctx.author.id)
        if session is None:
            conn = await self.pool.acquire()
            query = "SELECT * FROM infinite WHERE $1 IN (ventie, venter)"
            data = await conn.fetchrow(query, ctx.author.id)
            if data is None:
                return
            session = Session.from_record(self.pool, data)
            await self.pool.release(conn)

        user, alias = session.get_partner(ctx.author.id)
        channel = self.bot.get_channel(594256215119364317)
        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.add_field(name="Reported User ID", value=str(user))
        embed.add_field(name="Alias", value=alias)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=session.date.strftime("session time | %m/%d/%Y - %H:%M:%S"))
        if ctx.message.attachments:
            urls = [a.url for a in ctx.message.attachments[:5]]
            embed.add_field(name="Attachments:", value='\n'.join(urls))
        await channel.send(embed=embed)
        msg = "report successfully submitted"
        await ctx.channel.send(embed=utils.embed_confirm(msg))


def setup(bot):
    bot.add_cog(Engine(bot))
