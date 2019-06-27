from discord.ext import commands
from utils import NoMod


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_check(self, ctx):
        if not self.mod_check(ctx.author.id):
            raise NoMod
        return True

    async def mod_check(self, user_id):
        pass


def setup(bot):
    bot.add_cog(Mod(bot))
