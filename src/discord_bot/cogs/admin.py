import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import CheckFailure
from discord.ext.commands import ExtensionNotLoaded , ExtensionNotFound
from src.env_config import config

class AdminPanel(commands.Cog):
    """
    Admin commands for the bot.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    '''def is_admin(self, interaction : Interaction):
        return interaction.user.id == self.admin_id'''
    def is_admin():
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == config.ADMIN_ID
        return app_commands.check(predicate)

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="killswitch",description="goodbye bot")
    @is_admin()
    async def killswitch(self,interaction: discord.Interaction):
        await interaction.response.send_message('# BOT IS OFFLINE')
        await self.bot.close()

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='kill_book', description='burn the book')
    @is_admin()
    async def kill_book(self,interaction: discord.Interaction):
        target_cog = "src.discord_bot.cogs.book"
        await interaction.response.defer(ephemeral=True)
        if target_cog in self.bot.extensions:
            await self.bot.unload_extension(target_cog)
            await (await interaction.original_response()).edit(content="Unloaded Extension - Book",delete_after=15)
        else:
            print('Admin panel unload error.')
        

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name='refresh_bookie',description="Just dont touch it")
    @is_admin()
    async def refresh_book_cog(self,interaction: discord.Interaction):
        target_cog = "src.discord_bot.cogs.book"
        await interaction.response.send_message("Refreshing...",ephemeral=True, delete_after=15)
        try:
            if target_cog in self.bot.extensions:
                await self.bot.reload_extension(target_cog)
            else:
                await self.bot.load_extension(target_cog)
            await interaction.edit_original_response(content="Reloaded")
        except Exception as e:
            print(f"reload error - {e}")
            
    
    @refresh_book_cog.error
    @killswitch.error
    async def unauthorized_error(interaction: discord.Interaction,error):
        if isinstance(error,CheckFailure):
            await interaction.response.send_message("You have no power here." , ephemeral=True,delete_after=15)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminPanel(bot))