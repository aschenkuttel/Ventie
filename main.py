from discord.ext import commands
from config import TOKEN
import discord

bot = commands.Bot(command_prefix='.')
bot.owner_id = 211836670666997762
extensions = ['engine', 'admin', 'mod', 'listen']


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="everyone.")
    await bot.change_presence(activity=activity)


if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(f"cogs.{extension}")

bot.run(TOKEN)
