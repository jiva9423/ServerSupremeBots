import discord
from discord.ext import commands
import SharedFiles.firebase_db as firebase_db
import math


# create a class with what ever name you want.
class Inventory(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    # COMMANDS GO HERE
    # Use @commands instead of @client
    # for listeners @commands.Cog.listener()
    @commands.command(name="inv")
    async def show_inv(self, context, page_number=1):
        user_id = context.author.id
        inv = firebase_db.get_inventory(user_id)
        if not str(page_number).isnumeric():
            page_number = 1

        starting_index = 5 * (int(page_number)-1)# starting item for page
        inv_keys = list(inv.keys())
        if len(inv) == 0:
            await context.send("You don't have anything in your inventory")
            return
        max_pages = math.ceil(len(inv)/5)
        if starting_index >= len(inv):
            await context.send("page " + str(page_number) + " doesn't exist there are only " + str(max_pages))
            return

        # set up embed description
        description = ""
        for i in range(starting_index, starting_index+5):
            if i >= len(inv):
                break
            item = firebase_db.get_an_item(inv_keys[i])
            item_type = item.get("item_type")


            description += str(item.get("emoji")) + " **" + str(item.get("item_name")) + "** ─ " + str(inv.get(inv_keys[i])) + "\n"
            description += "ID `" + str(inv_keys[i]) + "` ─ " + item_type.capitalize() + "\n\n"

        my_embed = discord.Embed(title=str(context.author.name) + "'s Inventory", description=description, color=discord.Color.blue())
        my_embed.set_footer(text="Page " + str(page_number) + " of " + str(max_pages))
        await context.send(embed=my_embed)


# set it up
def setup(client):
    client.add_cog(Inventory(client))