import random
import discord
from discord.ext import commands

div = ["sleepy", "tiny", "cute", "red", "blue", "yellow"]
sub = ["Elefant", "Lobster", "Magician", "Carnivore"]


class AlreadyQueued(commands.CheckFailure):
    pass


class NotQueued(commands.CheckFailure):
    pass


class ActiveSession(commands.CheckFailure):
    pass


def confirm(msg, title="", status=""):
    embed = discord.Embed(color=discord.Color.green(), title=title, description=msg)
    embed.set_footer(text=status)
    return embed


class Anon:
    def __init__(self, user, alias):
        self.user = user
        self.id = user.id
        self.send = user.send
        self.alias = alias

    @property
    def args(self):
        return self.id, self.alias


def random_nick():
    return f"{random.choice(div)} {random.choice(sub)}"
