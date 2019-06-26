from config import database, db_key, db_user, host
from discord.ext import commands, tasks
from pool import Queue
import datetime
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

    @tasks.loop(seconds=3.0)
    async def cardinal(self):
        if self.pool is None:
            return
        result = self.queue.get_pair()
        if not result:
            return
        await self.create_session(*result)
        await self.intro(*result)

    @cardinal.before_loop
    async def before_cardinal(self):
        await self.bot.wait_until_ready()

    async def setup(self):
        conn_data = {"host": host, "port": "5432", "user": db_user,
                     "password": db_key, "database": database, "loop": self.bot.loop}
        self.pool = await asyncpg.create_pool(**conn_data)
        await self.load_cache()
        self.queue = Queue()

    async def create_session(self, ventie, venter):
        conn = await self.pool.acquire()
        query = "SELECT DISTINCT id FROM session, infinite ORDER BY DESC"
        data = await conn.fetch(query)
        id_ = data[0] + 1 if data else 1
        date = datetime.datetime.now()
        query = "INSERT INTO session" \
                "(id, ventie, big, venter, small, date, active)" \
                "VALUES ($1, $2, $3, $4, $5, $6, &7)"
        arguments = [id_, *ventie.args, *venter.args, date]
        await conn.execute(query, *arguments)
        await self.pool.release(conn)
        session = {'id': id_, 'date': date,
                   'ventie': {'id': ventie.id, 'alias': ventie.alias},
                   'venter': {'id': venter.id, 'alias': venter.alias}}
        self.sessions[id_] = session

    async def load_cache(self):
        conn = await self.pool.acquire()
        query = "SELECT * FROM session"
        data = await conn.fetch(query)
        await self.pool.release(conn)
        for record in data:
            session = {'id': record.id, 'date': record.date,
                       'ventie': {'id': record.ventie, 'alias': record.ventie_nick},
                       'venter': {'id': record.venter, 'alias': record.venter_nick}}
            self.sessions[record.id] = session

    async def active_session(self, user):
        active_user = []
        for session in self.sessions:
            active_user.append(session['ventie']['id'])
            active_user.append(session['venter']['id'])
        return user.id in active_user

    async def intro(self, ventie, venter):
        pass

    @commands.command(name="vent", aliases=["listen"])
    async def vent_(self, ctx, alias=None):

        if self.active_session(ctx.author):
            raise utils.ActiveSession

        status = False
        if ctx.invoked_with == "vent":
            status = True

        alias = alias if alias else utils.random_nick()

        user = utils.Anon(ctx.author, alias)
        self.queue.add_user(user, status)
        title = "Successfully added to queue!"
        msg = f"**Nickname:** `{alias}`"
        await ctx.author.send(embed=utils.confirm(msg, title, self.queue.status))


def setup(bot):
    bot.add_cog(Engine(bot))
