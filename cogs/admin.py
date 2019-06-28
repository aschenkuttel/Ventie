from discord.ext import commands
import utils


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()

    @commands.command(name="promote")
    async def promote_(self, ctx, user_id: int):
        conn = await self.pool.acquire()
        query = "SELECT * FROM mods WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        if result:
            msg = "user already mod"
            return await ctx.send(embed=utils.embed_error(msg))

        query = "INSERT INTO mods(id) VALUES ($1)"
        await conn.execute(query, user_id)
        await self.pool.release(conn)
        msg = "user has now mod permissions"
        await ctx.send(embed=utils.embed_confirm(msg))

    @commands.command(name="demote")
    async def demote_(self, ctx, user_id):
        conn = await self.pool.acquire()
        query = "SELECT * FROM mods WHERE id = $1"
        result = await conn.fetchrow(query, user_id)
        if result is None:
            msg = "user is no mod"
            return await ctx.send(embed=utils.embed_error(msg))

        query = "INSERT INTO mods(id) VALUES ($1)"
        await conn.execute(query, user_id)
        await self.pool.release(conn)
        msg = "user lost his mod permissions"
        await ctx.send(embed=utils.embed_confirm(msg))


def setup(bot):
    bot.add_cog(Admin(bot))
