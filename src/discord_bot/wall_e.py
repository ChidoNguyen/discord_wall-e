import discord
from discord.ext import commands
#config
from src.env_config import config
#utils
from src.discord_bot.utils.discord_bot_util import get_bot_cogs


###Bot Persmissions###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
#######################

bot = commands.Bot(command_prefix='!',intents=intents)


async def load_cogs():
    to_be_loaded = get_bot_cogs(cogs_path=config.DISCORD_COGS)
    if to_be_loaded:
        for cog in to_be_loaded:
            await bot.load_extension(cog)
    
@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f'Logged in as {bot.user} in {guild.name}')
    await bot.tree.sync()
    print("Current loaded cogs: ",list(bot.cogs.keys()))

async def main():
    async with bot:
        await load_cogs()
        await bot.start(config.DISCORD_TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run((main()))