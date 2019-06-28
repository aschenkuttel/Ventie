from discord.ext import commands
import random
import discord

div = ["sleepy", "red", "blue", "yellow", "young",
       "little", "good", "early", "calm", "clean"]
sub = ["Cat", "Lobster", "Magician", "Hero", "President",
       "Manager", "Tiger", "Eagle", "Star", "Duck"]


def random_nick():
    return f"{random.choice(div)} {random.choice(sub)}"


def embed_confirm(msg, title="", status=""):
    embed = discord.Embed(color=discord.Color.green(), title=title, description=msg)
    embed.set_footer(text=status)
    return embed


def embed_intro(participants):
    welcome = "Welcome to your session! Be friendly and whatever blah blah"
    embed = discord.Embed(title=f"User: {' - '.join([u.alias for u in participants])}",
                          description=welcome)
    footer = "Leave the session with .leave | report your session partner with .report"
    embed.set_footer(text=footer)
    return embed


def embed_error(msg):
    return discord.Embed(color=discord.Color.red(), description=msg)


class StillBanned(commands.CheckFailure):
    def __init__(self, days):
        self.days = days + 1


class NotBanned(commands.CheckFailure):
    pass


class AlreadyQueued(commands.CheckFailure):
    pass


class NotQueued(commands.CheckFailure):
    pass


class ActiveSession(commands.CheckFailure):
    pass


class NoSession(commands.CheckFailure):
    pass


class NoMod(commands.CheckFailure):
    pass
