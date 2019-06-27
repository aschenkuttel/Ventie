from discord.ext import commands
import utils


class Listen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.PrivateMessageOnly):
            msg = str(error)
        elif isinstance(error, utils.AlreadyQueued):
            msg = "Already in queue"
        elif isinstance(error, utils.NotQueued):
            msg = "Not in queue"
        elif isinstance(error, utils.NotQueued):
            msg = "Already in session"
        elif isinstance(error, utils.NoSession):
            msg = "You're currently in no session"
        elif isinstance(error, utils.NoMod):
            msg = "Command only invokable by mods"
        else:
            msg = str(error)
        embed = utils.embed_error(msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Listen(bot))
