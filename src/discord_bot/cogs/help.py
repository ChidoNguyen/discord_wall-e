import discord.interactions
import discord
from discord import app_commands
from discord.ext import commands
#from discord.ui import View,Button


###########
class PingView(discord.ui.View):
    """View containing buttons for selecting ping count."""
    def __init__(self):
        super().__init__()

        # Create buttons dynamically for 1-5 pings
        for i in range(1, 6):
            self.add_item(PingButton(label=str(i), count=i))

class PingButton(discord.ui.Button):
    """Button that sends multiple pings based on its label."""
    def __init__(self, label: str, count: int):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.count = count

    async def callback(self, interaction: discord.Interaction):
        """Handles button clicks and responds with multiple pings."""
        latency = round(interaction.client.latency * 1000, 2)
        response = "\n".join(["Pong! Latency: {}ms".format(latency)] * self.count)
        await interaction.response.send_message(response, ephemeral=True)
############
class BotHelp(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.abilities = [
            "Book - Does book stuff.",
            "TBD - TEE BEE DEE"
        ]

    @app_commands.command(name="help" ,description="The bot reveals itself to you semi-intimately.")
    async def help(self, interaction: discord.Interaction):
        #user_name = interaction.user.name
        multi_line_response = '\n'.join(self.abilities)
        await interaction.response.send_message(multi_line_response)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Responds with Pong!"""
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        temp_view = PingView()
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms" , view = temp_view)


async def setup(bot):
    await bot.add_cog(BotHelp(bot))
