import discord
from discord.ext import commands
import SharedFiles.firebase_db as firebase_db
import SharedFiles.fb_tokens as fb_tokens
import asyncio


def has_permissions(context):
    if context.author.id != fb_tokens.get_j_id() and context.author.id != fb_tokens.get_go_id():
        return False
    return True


async def add_item_helper(self, context):
    if not has_permissions(context):
        await context.reply("You don't have permission to perform this action")
        return

    def check(msg):
        return msg.author == context.author and msg.channel == context.channel

    tout = 120  # time out time
    # code
    try:
        await context.reply("Enter an item id. This will be used to find the item in the database:")
        item_id = await self.client.wait_for("message", check=check, timeout=tout)
        item_id = item_id.content
        item_id = str(item_id).lower()

        await context.reply("Enter item name:")
        item_name = await self.client.wait_for("message", check=check, timeout=tout)
        item_name = item_name.content

        await context.reply("Enter item description:")
        description = await self.client.wait_for("message", check=check, timeout=tout)
        description = description.content

        await context.reply("Enter item emoji:")
        emoji = await self.client.wait_for("message", check=check, timeout=tout)
        emoji = emoji.content

        await context.reply("Enter item buy price. Enter a number < 0 to make it not buyable:")
        buy_price = await self.client.wait_for("message", check=check, timeout=tout)
        buy_price = buy_price.content
        # make sure a number was entered
        try:
            int(buy_price)
        except ValueError:
            await context.reply("I'm sorry dude, but you need to enter a number. Item not created.")
            return

        await context.reply("Enter item sell price. Enter a number < 0 to make it not sellable:")
        sell_price = await self.client.wait_for("message", check=check, timeout=tout)
        sell_price = sell_price.content
        # make sure a number was entered
        try:
            int(sell_price)
        except ValueError:
            await context.reply("I'm sorry dude, but you need to enter a number. Item not created.")
            return

        await context.reply("Enter item type:")
        item_type = await self.client.wait_for("message", check=check, timeout=tout)
        item_type = item_type.content

        await context.reply("Enter a value 1 (very common) to 100 (extremely rare) for item rarity")
        item_rarity = await self.client.wait_for("message", check=check, timeout=tout)
        item_rarity = item_rarity.content

        if not item_rarity.isnumeric():
            await context.reply("I'm sorry dude, but you need to enter a number. Item not created.")
            return

        await context.reply("Overwrite any existing items with this id? (y, n):")
        overwrite = await self.client.wait_for("message", check=check, timeout=tout)
        overwrite = overwrite.content

        if overwrite == "y":
            overwrite = True
            temp_overwrite = "Yes"
        elif overwrite == "n":
            overwrite = False
            temp_overwrite = "No"
        else:
            await context.reply("You didn't enter a valid response. Item not created.")
            return

        embed_desc = "**id:** " + str(item_id) + \
                     "\n**name:** " + str(item_name) + \
                     "\n**description:** " + str(description) + \
                     "\n**emoji:** " + str(emoji) + \
                     "\n**buy price:** " + str(buy_price) + \
                     "\n**sell price:** " + str(sell_price) + \
                     "\n**type:** " + str(item_type) + \
                     "\n**rarity:** " + str(item_rarity) + \
                     "\n**overwrite:** " + str(temp_overwrite)

        embed = discord.Embed(
            title="Item Overview",
            description=embed_desc,
            color=discord.Color.blue())

        await context.reply("Is this item ok **(y, n)**:", embed=embed)
        is_item_ok = await self.client.wait_for("message", check=check, timeout=tout)  # 30 seconds to reply

        if is_item_ok.content == "y":
            added = firebase_db.add_item(item_id, item_name, description, emoji, int(buy_price), int(sell_price),
                                         item_type, item_rarity, overwrite)
            # return 1 if item added successfully with an item overwrite (item existed already and was replaced)
            # return 0 if item added successfully with no item overwrite.
            # return -1 if trying to overwrite an item when overwrite is set to False
            # return -2 if invalid type were included in the item_type list
            if added == 1:
                await context.reply("item with id " + item_id + " was successfully overridden in the database")
            elif added == 0:
                await context.reply(item_name + " item was successfully added to the database with the id " + item_id)
            elif added == -1:
                await context.reply("Failed to add item. "
                                    "You are trying to overwrite an existing item with the id " + item_id)
            elif added == -2:
                await context.reply(str(item_type) + " is not a valid type. No item was added")

    except asyncio.TimeoutError:
        await context.reply("Sorry, you didn't reply in time! Item not created")


async def add_item_type_helper(self, context):
    if not has_permissions(context):
        await context.reply("You don't have permission to perform this action")
        return

    def check(msg):
        return msg.author == context.author and msg.channel == context.channel

    tout = 30
    # code
    try:
        await context.reply("Enter an item type to add to the database:")
        item_type = await self.client.wait_for("message", check=check, timeout=tout)  # 30 seconds to reply
    except asyncio.TimeoutError:
        await context.reply("Sorry, you didn't reply in time! Item type not created")

    added = firebase_db.add_item_type(str(item_type.content))
    if added == 0:
        await context.message.channel.send(str(item_type.content) + " item type added to database.")
    elif added == -1:
        await context.message.channel.send(str(item_type.content) + " already exists in the database.")


async def remove_item_type_helper(self, context):
    if not has_permissions(context):
        await context.reply("You don't have permission to perform this action")
        return

    def check(msg):
        return msg.author == context.author and msg.channel == context.channel

    tout = 30
    # code
    try:
        await context.reply("Enter an item type to remove from the database:")
        item_type = await self.client.wait_for("message", check=check, timeout=tout)
        item_type = item_type.content
        removed = firebase_db.remove_item_type(item_type)
        if removed == 0:
            await context.reply("Item type " + item_type + " removed from the database.")
        elif removed == -1:
            await context.reply("Item type " + item_type + " does not exist in the database.")
    except asyncio.TimeoutError:
        await context.reply("Sorry, you didn't reply in time! Item type not created")


async def remove_item_helper(self, context):
    if not has_permissions(context):
        await context.reply("You don't have permission to perform this action")
        return

    def check(msg):
        return msg.author == context.author and msg.channel == context.channel

    tout = 30
    # code
    try:
        await context.reply("Enter an item id to remove an item from the database:")
        item_id = await self.client.wait_for("message", check=check, timeout=tout)
        item_id = item_id.content
        removed = firebase_db.remove_item(item_id)
        if removed == 0:
            await context.reply("Item with id " + item_id + " removed from the database.")
        elif removed == -1:
            await context.reply("Item with id " + item_id + " does not exist in the database.")
    except asyncio.TimeoutError:
        await context.reply("Sorry, you didn't reply in time! Item type not created")
    return


# create a class with what ever name you want.
class Items(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    # COMMANDS GO HERE
    # Use @commands.command() instead of @client.command()
    # for listeners @commands.Cog.listener()

    @commands.command(name="add")
    async def add_to_db(self, context, option):
        if option == "type":
            await add_item_type_helper(self, context)
        elif option == "item":
            await add_item_helper(self, context)
        else:
            await context.message.channel.send(str(option) + " is not valid.")

    @commands.command(name="remove")
    async def remove_from_db(self, context, option):
        if option == "type":
            await remove_item_type_helper(self, context)
        elif option == "item":
            await remove_item_helper(self, context)
        else:
            await context.message.channel.send(str(option) + " is not valid.")


# set it up
def setup(client):
    client.add_cog(Items(client))
