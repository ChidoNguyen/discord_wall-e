import discord
import os

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DiscordToken = os.getenv("DISCORD_TOKEN")

###Bot Persmissions###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
#######################

bot = commands.Bot(command_prefix='!',intents=intents)

async def load_cogs():
    await bot.load_extension("src.discord.cogs.book")
    print(list(bot.cogs.keys()))
@bot.event
async def on_ready():
    server_name = discord.utils.get(bot.guilds)
    print(f'Logged in as {bot.user} in {server_name}.')
    await bot.tree.sync()
@bot.command()
async def list_commands(ctx):
    commands = await bot.tree.fetch_commands()  # Fetch all registered global commands
    if commands:
        await ctx.send(f"Global commands: {[cmd.name for cmd in commands]}")
    else:
        await ctx.send("No global commands found. Your bot might be using guild-specific commands.")
async def main():
    async with bot:
        await load_cogs()
        await bot.start(DiscordToken)

if __name__ == '__main__':
    import asyncio
    asyncio.run((main()))