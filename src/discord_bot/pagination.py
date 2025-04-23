import discord
import discord.interactions
from discord.ui import View, Button
import os
from dotenv import load_dotenv
load_dotenv()
THE_VAULT = os.getenv('THE_VAULT')

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
            if self.cur_page < -(-len(self.data)//self.per_page) - 1:
                self.cur_page += 1
                self.next_page.disabled = (self.cur_page == -(-len(self.data)//self.per_page) - 1)
                self.prev_page.disabled = (self.cur_page == 0)
                embed_view = self.create_catalog_embed()
                await self.refresh_select_drop()
                await interaction.response.edit_message(embed=embed_view,view=self)
        except Exception as e:
            print(e)
            pass
    
    async def select_pick_callback(self, interaction: discord.Interaction):
            selected = interaction.data['values'][0]
            try:
                import json
                import io
                selected = json.loads(selected)
                full_title = selected['full title'] + '.epub'
                full_path = os.path.join(THE_VAULT,full_title)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as file:
                        file_bytes = io.BytesIO(file.read())
                    file_bytes.seek(0)
                    attached_file = discord.File(fp=file_bytes,filename=full_title)
                    await interaction.response.send_message(content='As requested.',file=attached_file)
            except Exception as e:
                print(e)
                await interaction.response.send_message("Failed loading old catalog choice.")
                pass

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
        import random
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
        for (id_,fname,lname,title) in target_data:
            author = f'{fname} {lname}'.strip()
            select_label = f"{title} by {author}"
            selectOpt_object = discord.SelectOption(label=select_label,value=f'{{"id" : "{id_}", "full title" : "{select_label}"}}',emoji=random.choice(book_emojis),)
            selectOpts.append(selectOpt_object)
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
            id_ , fname, lname , title = items
            author = f'{fname} {lname}'.strip()
            embed_obj.add_field(
                name='',
                #value= f'**`{title} by {author}`**',
                value=f'_{title}_\u2003`by`\u2003**{author}**',
                inline=False
            )
        return embed_obj