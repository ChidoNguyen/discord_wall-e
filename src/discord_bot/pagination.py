import discord
import discord.interactions
from discord.ui import View, Button
import random
import os
from src.fastAPI.catalog_cache import FileInfo , CacheResult

from src.env_config import config
#THE_VAULT = config.THE_VAULT

class PaginatorView(View):
    """
    NOTE !! Discord view has restrictions check before you edit too much for displaying and what not !!

    PaginatorView is the "fake it till you make it" approach to pretend to have iframe in discord Bot. Pagination to scroll through catalog.

    Args:
        data : dict of data we retrieve from cache file, key should be 'catalog'
        interaction : discord.Interaction that triggered this command
        per_page : set to 10 , # of items to display per page/view
        timeout : set to 120s , duration before we expire the view
    Attributes:
        per_page : number of items to display per view page
        interaction : interaction that triggered view
        cur_page : current page starts at 0
        max_pages : max pages we can display based on our data and per_page values

    """
    def __init__(
            self,
            data,
            interaction : discord.Interaction,
            *,
            per_page = 10,
            timeout = 120
    ):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        #data
        cache_data = self._rebuild_cache_data(data)
        self.data_id_map= cache_data.id_map
        self.data_id_list= cache_data.id_list
        #pages
        self.per_page = per_page
        self.cur_page = 0
        total = len(self.data_id_list)
        self.max_pages = max((total - 1)//self.per_page , 0)
        #select module#
        self.select_drop_menu = None
        self.refresh_select_drop()

    @staticmethod
    def _rebuild_cache_data(data : dict) -> CacheResult:
        """
        Reconstructs custom dataclass CacheResult from serialized data.

        This function rebuilds custom dataclass `CacheResult` object form cache data. Data was converted to JSON for storage. Original data structure was constructed with 2 custom dataclass `CacheResult` and `FileInfo.

        Args:
            data(dict) : 
                -id_map (Mapping[int,FileInfo]): A read-only map-like object that maps id integers to FileInfo objects. Mapping[int,FileInfo]
                -id_list (list): List of integer IDs
        
        Returns:
            CacheResult : A reconstructed instance of CacheResult
        """
        cache_info = CacheResult(
            id_map = {
                int(key): FileInfo(**value) for (key,value) in data['id_map'].items()
            },
            id_list = data['id_list']
        )
        return cache_info
    
    async def on_timeout(self):
        """ Clears all views and options. """
        og_message = await self.interaction.original_response()
        await og_message.edit(embed = None ,view = None, content="Move along nothing to see here.")

    def id_lookup(self, opt_id) -> FileInfo:
        """ Returns FileInfo object for related ID from id_map """
        return self.data_id_map[int(opt_id)]
        

    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        """
        `Back` button to emulate dynamic embed page changes
        """
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == self.max_pages)
            embed_view = self.create_catalog_embed()
            self.refresh_select_drop()
            await interaction.response.edit_message(embed=embed_view,view = self)

    @discord.ui.button(label='▶️',style=discord.ButtonStyle.grey)
    async def next_page(self , interaction :discord.Interaction, button : Button):
        """
        `Forward` button to emulate dynamic embed page changes
        """
        if self.cur_page < self.max_pages:
            self.cur_page += 1
            self.next_page.disabled = (self.cur_page == self.max_pages)
            self.prev_page.disabled = (self.cur_page == 0)
            embed_view = self.create_catalog_embed()
            self.refresh_select_drop()
            await interaction.response.edit_message(embed=embed_view,view=self)
    
    @discord.ui.button(label='❌', style = discord.ButtonStyle.grey)
    async def clear_catalog(self , interaction : discord.Interaction, button : Button):
        ''' Cancel button clears out views and options. '''
        #clear embed view
        trash_emojis = [
            "🗑️",  # Trash can
            "🚮",  # Litter in bin sign
            "❌",  # Cross mark
            "🧹",  # Broom
            "🧼",  # Soap
            "🔥",  # Fire
            "💣",  # Bomb
            "💥",  # Collision
            "♻️",  # Recycle
            "🧻",  # Toilet paper
            "🧺"   # Basket
        ]

        await interaction.response.edit_message(
            content=random.choice(trash_emojis),
            embed=None,
            view=None
        )
        self.stop()

    async def select_pick_callback(self, interaction: discord.Interaction):
            '''
            Custom Callback to handle when an option is chosen from dropdown menu.

            Option stores ID value relating to the choice. Function will retrieve FileInfo from id_map instance. 
            '''
            import io
            try:
                await interaction.response.send_message("🔎",ephemeral=True,delete_after=75)
                og_response = await interaction.original_response()

                selected_id = interaction.data['values'][0]
                option = self.id_lookup(selected_id)
                selected_file = os.path.join(os.path.join(config.THE_VAULT,'the_goods'),option.filename)

                if os.path.exists(selected_file):
                    with open(selected_file,'rb') as file:
                        file_bytes = io.BytesIO(file.read())
                    file_bytes.seek(0)
                    attached_file = discord.File(fp=file_bytes,filename=option.filename)
                    await og_response.edit(content=f"✅ message and file attachment will self delete in 60s.{interaction.user.mention}",attachments=[attached_file])
            except Exception as e:
                print(f'{e}')
                await og_response.edit(content='Something went wrong.{interaction.user.mention}')



    def refresh_select_drop(self):
        ''' Updates drop down menu to reflect embed view. '''
        try:
            #gates to only remove if we already have a menu
            if hasattr(self,"select_drop_menu") and self.select_drop_menu is not None:
                self.remove_item(self.select_drop_menu)
            self.select_drop_menu = self.select_options()
            self.add_item(self.select_drop_menu)
            self.select_drop_menu.callback = self.select_pick_callback
        except Exception as e:
            print(f"Error refreshing drop down - {e}")

    def select_options(self) -> discord.ui.Select:
        """
        Generates the available options for user to pick.

        Iterates through the the items that are suppose to be displayed for target page and creates SelectOption objects for each.
        Note:
            SelectOptions : 
                label : formatted string truncated -> discord restriction 100 max char f'{FileInfo.title} by {FileInfo.author}'[:100]
                value : integer ID 
                emoji - optional dealers choice
        Returns:
            discord.Select object created with the SelectionOptions
        """
        #options are tied to embed view of current page
        offset = self.per_page * self.cur_page
        start = 0 + offset
        end = self.per_page + offset
        target_data = self.data_id_list[start:end]
        book_emojis = [
            #"📚",  # Books - stack of books
            #"📖",  # Open Book
            "📕",  # Closed Red Book
            "📗",  # Green Book
            "📘",  # Blue Book
            "📙",  # Orange Book
            "📒",  # Ledger
            "📓",  # Notebook
            "📔",  # Notebook with Cover
            "📜",  # Scroll
            "📄",  # Page Facing Up
            "📃",  # Page with Curl
            "📑",  # Bookmark Tabs
            "🔖",  # Bookmark
        ]
        # id , fname, lname , title 
        selectOpts = []
        for opt_id in target_data:
            option = self.id_lookup(opt_id)
            if option is None:
                continue
            rng_emote=random.choice(book_emojis)
            select_label = f'{option.title} by {option.author}'
            selectOpt_object = discord.SelectOption(label=select_label[:100],value=opt_id,description=option.author,emoji=rng_emote)
            selectOpts.append(selectOpt_object)

        return discord.ui.Select(placeholder="What do you want?", options=selectOpts)

    def create_catalog_embed(self) -> discord.Embed:
        """
        Generates the embed view for the current page.

        View is formatted text string assigned to the current embed object as a field. 

        Returns:
            discord.Embed object for rendering
        """
        #10 items per page
        offset = self.cur_page * self.per_page
        start = 0 + offset
        end = self.per_page + offset

        embed_title = "📚 Catalog"
        embed_obj = discord.Embed(title=embed_title)

        for opt_id in self.data_id_list[start:end]:
            #id , fname , lname , title
            #id_ , fname, lname , title = items
            #author = f'{fname} {lname}'.strip()
            option = self.id_lookup(opt_id)
            if option is None:
                continue
            embed_obj.add_field(
                name='',
                #value= f'**`{title} by {author}`**',
                value=f'**{option.title}**\u2003`by`\u2003_{option.author}_',
                inline=False
            )
        return embed_obj