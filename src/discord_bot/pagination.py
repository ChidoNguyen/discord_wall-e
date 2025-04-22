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

    title = 'Catalog'
    embed_obj = discord.Embed(title=title)

    # fields build a column , parse out our DB row info by columns
    item_id , auth , title = [] , [] , []

    for row_id , row_fname, row_lname , row_title  in data[start:end]:
        author = f'{row_fname} {row_lname}'
        item_id.append(str(row_id))
        auth.append(author.strip())
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

    embed_obj.set_footer(text=f'Page {page + 1} of {-(-len(data)//items_per)}')

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

        #select module#
        self.select = self.select_options()
        self.add_item(self.select)

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
        
    def select_options(self):
        #options are tied to embed view of current page
        offset = self.per_page * self.cur_page
        start = 0 + offset
        end = self.per_page + offset
        target_data = self.data[start:end]

        # id , fname, lname , title 
        selectOpts = []
        for (id,fname,lname,title) in target_data:
            select_label = f'Option {id} : {title}'
            selectOpt_object = discord.SelectOption(label=select_label,value=id)
            selectOpts.append(selectOpt_object)
        return discord.ui.Select(placeholder="What do you want?", options=selectOpts)

