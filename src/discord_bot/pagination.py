import discord
import discord.interactions
from discord.ui import View, Button
import random
import os
from src.fastAPI.catalog_cache import FileInfo , CacheResult
from dotenv import load_dotenv
load_dotenv()
THE_VAULT = os.getenv('THE_VAULT')
'''
data items are id mappings id : {fname , lname , author , title , file name}
'''
def cache_result_transform(data) -> CacheResult:
    cache_results=CacheResult(
            id_map = { int(key) : FileInfo(**value) for (key,value) in data['id_map'].items()},
            id_list = data['id_list']
            )
    return cache_results.id_map , cache_results.id_list

class PaginatorView(View):
    
    def __init__(
            self,
            data,
            interaction : discord.Interaction,
            per_page = 10,
            timeout = 120
    ):
        super().__init__(timeout=timeout)
        self.data_id_map , self.data_id_list = cache_result_transform(data)

        self.per_page = per_page
        self.interaction = interaction
        self.cur_page = 0
        self.max_pages = -(-len(self.data_id_list)//self.per_page) - 1
        #select module#
        self.select_drop_menu = self.select_options()
        self.add_item(self.select_drop_menu)
        self.select_drop_menu.callback = self.select_pick_callback

    async def on_timeout(self):
        og_message = await self.interaction.original_response()
        await og_message.edit(embed = None ,view = None, content="Move along nothing to see here.")

    def id_lookup(self, opt_id) -> FileInfo:
        return self.data_id_map[int(opt_id)]
        

    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == self.max_pages)
            embed_view = self.create_catalog_embed()
            await self.refresh_select_drop()
            await interaction.response.edit_message(embed=embed_view,view = self)

    @discord.ui.button(label='▶️',style=discord.ButtonStyle.grey)
    async def next_page(self , interaction :discord.Interaction, button : Button):
        try:
            if self.cur_page < self.max_pages:
                self.cur_page += 1
                self.next_page.disabled = (self.cur_page == self.max_pages)
                self.prev_page.disabled = (self.cur_page == 0)
                embed_view = self.create_catalog_embed()
                await self.refresh_select_drop()
                await interaction.response.edit_message(embed=embed_view,view=self)
        except Exception as e:
            print(e)
            pass
    
    @discord.ui.button(label='❌', style = discord.ButtonStyle.grey)
    async def clear_catalog(self , interaction : discord.Interaction, button : Button):
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
            import io
            try:
                await interaction.response.send_message("🔎",ephemeral=True,delete_after=75)
                og_response = await interaction.original_response()

                selected = interaction.data['values'][0]
                option = self.id_lookup(selected)
                selected_file = os.path.join(os.path.join(THE_VAULT,'the_goods'),option.filename)
                if os.path.exists(selected_file):
                    with open(selected_file,'rb') as file:
                        file_bytes = io.BytesIO(file.read())
                    file_bytes.seek(0)
                    attached_file = discord.File(fp=file_bytes,filename=option.filename)
                    await og_response.edit(content=f"✅ message and file attachment will self delete in 60s.{interaction.user.mention}",attachments=[attached_file])
            except Exception as e:
                print(f'{e}')


    async def refresh_select_drop(self):
        self.remove_item(self.select_drop_menu)
        self.select_drop_menu = self.select_options()
        self.add_item(self.select_drop_menu)
        self.select_drop_menu.callback = self.select_pick_callback

    def select_options(self):
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

    def create_catalog_embed(self):
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