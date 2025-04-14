import discord
import discord.interactions
from discord.ui import View, Button

class PaginatorView(View):
    def __init__(
            self,
            pages : list[discord.Embed],
            timeout = 120
            ):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.cur_page = 0

    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == len(self.pages)-1)
            await interaction.response.edit_message(embed=self.pages[self.cur_page],view = self)
    @discord.ui.button(label='▶️',style=discord.ButtonStyle.grey)
    async def next_page(self , interaction :discord.Interaction, button : Button):
        if self.cur_page < len(self.pages) - 1:
            self.cur_page += 1
            self.next_page.disabled = (self.cur_page == len(self.pages)-1)
            self.prev_page.disabled = (self.cur_page == 0)
            await interaction.response.edit_message(embed=self.pages[self.cur_page],view=self)
        
