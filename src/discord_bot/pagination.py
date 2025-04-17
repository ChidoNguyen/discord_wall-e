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

    title = '# Catalog'
    embed_obj = discord.Embed(title=title)

    # fields build a column , parse out our DB row info by columns
    item_id , auth , title = [] , [] , []

    for row_id , row_auth , row_title  in data[start:end]:
        item_id.append(str(row_id))
        auth.append(row_auth)
        title.append(row_title)

    id_col = '\n'.join(item_id)
    auth_col = '\n'.join(auth)
    title_col = '\n'.join(title)

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
            per_page = 10,
            timeout = 120
    ):
        super().__init__(timeout=timeout)
        self.data = data
        self.per_page = per_page
        self.interaction = interaction
        self.cur_page = 0

    async def on_timeout(self):
        og_message = await self.interaction.original_response()
        await og_message.edit(embed = None ,view = None, content="Move along nothing to see here.")

    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == len(self.data)-1)
            embed_view = catalog_get_page_embed(self.cur_page,self.data)
            await interaction.response.edit_message(embed=embed_view,view = self)

    @discord.ui.button(label='▶️',style=discord.ButtonStyle.grey)
    async def next_page(self , interaction :discord.Interaction, button : Button):
        if self.cur_page < len(self.data) - 1:
            self.cur_page += 1
            self.next_page.disabled = (self.cur_page == -(-len(self.data)//self.per_page) - 1)
            self.prev_page.disabled = (self.cur_page == 0)
            embed_view = catalog_get_page_embed(self.cur_page,self.data)
            await interaction.response.edit_message(embed=embed_view,view=self)
        
