import asyncpg
from discord.ext import commands


class Engine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild:
            raise commands.PrivateMessageOnly
        return True

    @commands.command(name="vent")
    async def vent_(self, ctx):
        pass

    @commands.command(name="listen")
    async def listen_(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Engine(bot))
