import re
import datetime
from discord.ext import commands
from utils import NoMod
import discord
import utils


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        conn = await self.pool.acquire()
        query = "SELECT * FROM mods"
        data = await conn.fetch(query)
        mods = [r['id'] for r in data]
        await self.pool.release(conn)
        if ctx.author.id in mods:
            return True
        raise NoMod()

    @commands.command(name="session")
    async def session_(self, ctx, session_id: int):

        conn = await self.pool.acquire()
        query = "SELECT * FROM infinite WHERE id = $1"
        session = await conn.fetchrow(query, session_id)
        await self.pool.release(conn)

        if session is None:
            msg = "session not found"
            return await ctx.send(embed=utils.embed_error(msg))

        header = f"**Session {session['id']}**"
        ventie = f"**Ventie:** {session['ventie']}\n**Alias:** {session['ventie_alias']}"
        venter = f"**Venter:** {session['venter']}\n**Alias:** {session['venter_alias']}"
        date = session['date'].strftime("%m/%d/%Y - %H:%M:%S")
        data = f"{header}\n{ventie}\n{venter}"
        embed = discord.Embed(description=data)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)

    @commands.command(name="sessions")
    async def sessions_(self, ctx, user_id: int):
        conn = await self.pool.acquire()
        query = "SELECT * FROM infinite WHERE $1 IN (ventie, venter)"
        sessions = await conn.fetch(query, user_id)
        await self.pool.release(conn)

        if not sessions:
            msg = "no related sessions"
            return await ctx.send(embed=utils.embed_error(msg))

        user = self.bot.get_user(user_id)
        name = user.name if user else "not mutual server "
        header = f"**Username:** {name}"
        count = f"**sessions in total:** {len(sessions)}"
        last_5 = []
        for session in sessions[-5:]:
            state = session['ventie'] == user_id
            nick = session['ventie_alias'] if state else session['venter_alias']
            last_5.append(f"`{session['id']}` | {nick}")
        last_sessions = '\n'.join(last_5)
        date = sessions[-1]['date'].strftime("Last Session: %m/%d/%Y - %H:%M:%S")
        data = f"{header}\n{count}\n{last_sessions}"
        embed = discord.Embed(description=data)
        embed.set_footer(text=date)
        await ctx.send(embed=embed)

    @commands.command(name="ban")
    async def ban_(self, ctx, user_id: int, days: int):

        conn = await self.pool.acquire()
        query = "SELECT * FROM blacklist WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        if result:
            date = datetime.datetime.now()
            still = (result['till'] - date).days
            raise utils.StillBanned(still)

        date = datetime.datetime.now()
        till = date + datetime.timedelta(days=days)
        query = "INSERT INTO blacklist(id, begin, till) VALUES($1, $2, $3)"
        await conn.execute(query, user_id, date, till)
        await self.pool.release(conn)
        msg = f"user got banned for {days} days"
        await ctx.send(embed=utils.embed_confirm(msg))

    @commands.command(name="unban")
    async def unban_(self, ctx, user_id: int):

        conn = await self.pool.acquire()
        query = "SELECT * FROM blacklist WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        if result is None:
            raise utils.NotBanned()

        query = "DELETE FROM blacklist WHERE id = $1"
        await conn.execute(query, user_id)
        await self.pool.release(conn)
        msg = f"user got unbanned"
        await ctx.send(embed=utils.embed_confirm(msg))


def setup(bot):
    bot.add_cog(Mod(bot))
