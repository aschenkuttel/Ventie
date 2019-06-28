from discord.ext import commands
import utils


class Listen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.PrivateMessageOnly):
            msg = "commands only invokable in private message"
        elif isinstance(error, utils.AlreadyQueued):
            msg = "you're already in queue"
        elif isinstance(error, utils.NotQueued):
            msg = "you're currently not in queue"
        elif isinstance(error, utils.ActiveSession):
            msg = "you're already in an active session"
        elif isinstance(error, utils.NoSession):
            msg = "you're currently in no session"
        elif isinstance(error, utils.NoMod):
            msg = "command only invokable by mods"
        elif isinstance(error, utils.StillBanned):
            s = "s" if error.days > 1 else ""
            msg = f"still banned for {error.days} day{s}"
        elif isinstance(error, utils.NotBanned):
            msg = "user is not banned"
        else:
            return
        embed = utils.embed_error(msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Listen(bot))
