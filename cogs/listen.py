from discord.ext import commands
import utils


class Listen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(error)
        elif isinstance(error, utils.AlreadyQueued):
            await ctx.send("Already in queue")
        elif isinstance(error, utils.NotQueued):
            await ctx.send("Not in queue")
        elif isinstance(error, utils.NotQueued):
            await ctx.send("Already in session")
        else:
            await ctx.send(error)


def setup(bot):
    bot.add_cog(Listen(bot))
