import discord
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DiscordToken = os.getenv("DISCORD_TOKEN")
Janitors = int(os.getenv("JANITORS"))

###Bot Persmissions###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
#######################

bot = commands.Bot(command_prefix='!',intents=intents)

async def load_cogs():
    await bot.load_extension("src.discord.cogs.book")
    await bot.load_extension("src.discord.cogs.help")


@bot.event
async def on_ready():
    server_name = discord.utils.get(bot.guilds)
    print(f'Logged in as {bot.user} in {server_name}.')
    await bot.tree.sync(guild=discord.Object(id=Janitors))
    print(list(bot.cogs.keys()))


async def main():
    async with bot:
        await load_cogs()
        await bot.start(DiscordToken)

if __name__ == '__main__':
    import asyncio
    asyncio.run((main()))