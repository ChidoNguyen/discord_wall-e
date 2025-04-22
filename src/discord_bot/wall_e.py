import discord
import os

from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from discord.app_commands import CheckFailure

load_dotenv()
DiscordToken = os.getenv("DISCORD_TOKEN")
Admin_ID = int(os.getenv("ADMIN_ID"))
Janitors = int(os.getenv("JANITORS"))
Personal_Test = int(os.getenv("PERSONAL_TEST"))
###Bot Persmissions###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
#######################

bot = commands.Bot(command_prefix='!',intents=intents)
async def admin_check(interaction : discord.Interaction):
    return interaction.user.id == Admin_ID
async def load_cogs():
    await bot.load_extension("src.discord_bot.cogs.book")
    await bot.load_extension("src.discord_bot.cogs.help")


@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f'Logged in as {bot.user} in {guild.name}')
    #server_name = (discord.utils.get(bot.guilds,id=Janitors)).name
    #bot.tree.clear_commands(guild=discord.Object(id=Janitors))
    #print(f'Logged in as {bot.user} in {server_name}.')
    #await bot.tree.clear_commands()
    await bot.tree.sync()
    print("Current loaded cogs: ",list(bot.cogs.keys()))

@bot.tree.command(name="killswitch",description = "fail safe")
@app_commands.default_permissions(administrator=True)
@app_commands.check(admin_check)
async def kill_bot(interaction : discord.Interaction):
    await interaction.response.send_message('# BOT IS OFFLINE')
    await bot.close()
@kill_bot.error
async def unauthorized_error(interaction : discord.Interaction, error):
    if isinstance(error , CheckFailure):
        await interaction.response.send_message("You have no power here." , ephemeral=True , delete_after=15)
    else:
        await interaction.response.send_message("Something is extra broken...")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(DiscordToken)

if __name__ == '__main__':
    import asyncio
    asyncio.run((main()))