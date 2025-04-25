import discord
import discord.interactions
from discord.ui import View, Button
import random
import os
from dotenv import load_dotenv
load_dotenv()
THE_VAULT = os.getenv('THE_VAULT')
'''
data items are id mappings id : {fname , lname , author , title , file name}
'''
class PaginatorView(View):
    
    def __init__(
            self,
            data ,
            interaction : discord.Interaction,
            per_page = 10,
            timeout = 120
    ):
        super().__init__(timeout=timeout)
        self.data = data
        self.per_page = per_page
        self.interaction = interaction
        self.cur_page = 0
        self.max_pages = -(-len(self.data)//self.per_page) - 1
        #select module#
        self.select_drop_menu = self.select_options()
        self.add_item(self.select_drop_menu)
        self.select_drop_menu.callback = self.select_pick_callback

    async def on_timeout(self):
        og_message = await self.interaction.original_response()
        await og_message.edit(embed = None ,view = None, content="Move along nothing to see here.")


    @discord.ui.button(label='◀️',disabled=True,style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction : discord.Interaction, button : Button):
        if self.cur_page > 0:
            self.cur_page -= 1
            self.prev_page.disabled = (self.cur_page == 0)
            self.next_page.disabled = (self.cur_page == len(self.data)-1)
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
            import json
            import io
            await interaction.response.send_message("🔎",ephemeral=True,delete_after=75)
            og_response = await interaction.original_response()

            selected = interaction.data['values'][0]
            id_info = self.data[selected] 
            selected_file = os.path.join(os.path.join(THE_VAULT,'the_goods'),id_info.filename)
            if os.path.exists(selected_file):
                with open(selected_file,'rb') as file:
                    file_bytes = io.BytesIO(file.read())
                file_bytes.seek(0)
                attached_file = discord.File(fp=file_bytes,filename=id_info.filename)
                await og_response.edit(content=f"✅ message and file attachment will self delete in 60s.{interaction.user.mention}",attachments=[attached_file])
            '''selected = json.loads(selected)

            full_title = selected['full title'] + '.epub'
            full_path = os.path.join(THE_VAULT,full_title)

            if os.path.exists(full_path):
                with open(full_path, 'rb') as file:
                    file_bytes = io.BytesIO(file.read())
                file_bytes.seek(0)
                attached_file = discord.File(fp=file_bytes,filename=full_title)
                await og_response.edit(content=f"✅ message and file attachment will self delete in 60s.{interaction.user.mention}",attachments=[attached_file])'''


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
        target_data = self.data[start:end]
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
        for item in target_data:
            rng_emote=random.choice(book_emojis)
            select_label = f'{item.title} by {item.author}'
            selectOpt_object = discord.SelectOption(label=select_label[:100],value=item.id,description=item.author,emoji=rng_emote)
            selectOpts.append(selectOpt_object)

        """ for (id_,fname,lname,title) in target_data:
            rng_emote=random.choice(book_emojis)
            author = f'{fname} {lname}'.strip()
            select_label = f"{title} by {author}"
            selectOpt_object = discord.SelectOption(label=select_label,value=f'{id}**{select_label}',emoji=rng_emote)
            selectOpts.append(selectOpt_object) """
        return discord.ui.Select(placeholder="What do you want?", options=selectOpts)

    def create_catalog_embed(self):
        #10 items per page
        offset = self.cur_page * self.per_page
        start = 0 + offset
        end = self.per_page + offset

        embed_title = "📚 Catalog"
        embed_obj = discord.Embed(title=embed_title)

        for items in self.data[start:end]:
            #id , fname , lname , title
            #id_ , fname, lname , title = items
            #author = f'{fname} {lname}'.strip()
            embed_obj.add_field(
                name='',
                #value= f'**`{title} by {author}`**',
                value=f'**{items.title}**\u2003`by`\u2003_{items.author}_',
                inline=False
            )
        return embed_obj