from discord.ext import commands
from config import TOKEN
import discord

bot = commands.Bot(command_prefix='.')
extensions = ['engine', 'admin', 'mod', 'listen']


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="everyone!")
    await bot.change_presence(activity=activity)
    print("Ready to Vent!")


if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(f"cogs.{extension}")


bot.run(TOKEN)