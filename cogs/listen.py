from discord.ext import commands


class Listen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(Listen(bot))
