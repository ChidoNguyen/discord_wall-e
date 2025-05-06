import discord
from discord.ext import commands
from src.env_config import config



###Bot Persmissions###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
#######################

bot = commands.Bot(command_prefix='!',intents=intents)
async def admin_check(interaction : discord.Interaction):
    return interaction.user.id == config.ADMIN_ID
async def load_cogs():
    await bot.load_extension("src.discord_bot.cogs.book")
    await bot.load_extension("src.discord_bot.cogs.help")
    await bot.load_extension("src.discord_bot.cogs.admin")

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