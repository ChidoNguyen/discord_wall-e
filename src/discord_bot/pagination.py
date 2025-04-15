import discord
import discord.interactions
from discord.ui import View, Button

def catalog_get_page_embed(page : int , data : list[list[str]]):
    '''
    Function : returns a discord.Embed() object for rendering
    '''

    # title - titles our embed view
    # fields - used to generate the mock-up item listings
    # inline to side-by-side id-title-author
    
    items_per = 10
    start , end = 0 + (page * items_per) , items_per + (page * items_per)
    # our "data"  [ int , str , str ]
    # embed needs title 
    title = '# Catalog'
    embed_obj = discord.Embed(title=title)
    #each field can be displayed Vertically...
    #join each with new line \n
    #we have a range of our data start->end
    # we want to get id at index 0 
    #for i in range(start,end):
    #    id_col = '\n'.join(id_col,data[i][0]) # our id
    id_col = '\n'.join(str(id[0]) for id in data[start:end])
    auth_col = '\n'.join( info[1] for info in data[start:end])
    title_col = '\n'.join(info[2] for info in data[start:end])
    embed_obj.add_field(
        name = 'ID',
        value = id_col,
        inline=True
    )
    embed_obj.add_field(
        name = 'Title',
        value = title_col,
        inline = True
    )
    embed_obj.add_field(
        name = 'Author',
        value = auth_col,
        inline=True
    )
    return embed_obj
class PaginatorView(View):
    
    def __init__(
            self,
            data : list[list[str]],
            interaction : discord.Interaction,
            timeout = 120,
    ):
        super().__init__(timeout=timeout)
        self.data = data
        self.interaction = interaction
        self.cur_page = 0



    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == len(self.data)-1)
            await interaction.response.edit_message(embed=self.data[self.cur_page],view = self)

    @discord.ui.button(label='▶️',style=discord.ButtonStyle.grey)
    async def next_page(self , interaction :discord.Interaction, button : Button):
        if self.cur_page < len(self.pages) - 1:
            self.cur_page += 1
            self.next_page.disabled = (self.cur_page == len(self.data)-1)
            self.prev_page.disabled = (self.cur_page == 0)
            await interaction.response.edit_message(embed=self.data[self.cur_page],view=self)
        
