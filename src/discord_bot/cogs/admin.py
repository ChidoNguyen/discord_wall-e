import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import CheckFailure
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
    @app_commands.command(name='refresh_bookie',description="Just dont touch it")
    @is_admin()
    async def refresh_book_cog(self,interaction: discord.Interaction):
        target_cog = "src.discord_bot.cogs.book"
        await interaction.response.send_message("Refreshing...",ephemeral=True, delete_after=15)
        try:
            await self.bot.reload_extension(target_cog)
        except Exception as e:
            print(f"reload error - {e}")
            
    
    @refresh_book_cog.error
    @killswitch.error
    async def unauthorized_error(interaction: discord.Interaction,error):
        if isinstance(error,CheckFailure):
            await interaction.response.send_message("You have no power here." , ephemeral=True,delete_after=15)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminPanel(bot))