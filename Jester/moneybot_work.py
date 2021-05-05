# create method to be used in another file
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import random
from SharedFiles.firebase_db import add_wallet_bal, add_to_inventory, get_an_item, get_items_by_type, get_rarest_item, get_item_from_inventory

random_people = ["Random Stranger", "Your mom", "Your dad", "The King", "The Baron", "A Knight in Shining Armor", "Marco Polo", "That one dude", "Genghis Khan", "King Arthur", "Vlad the Impaler", "Leonardo DaVinci", "Some guy from the future", "Baker", "A horse", "Your mom's bf", "John", "John Cena", "A wild pokemon!", "That guy on the wanted posters", "Mr. Beast", "John", "Bob", "Bobalina", "Margaret"]
no_money_responses = ['Haha, imagine begging', 'My mommy told me not to give money to strangers', '*stares at you awkwardly*', 'Here you can have this: *nothing*.', 'Haha. No', 'Go away filthy beggar', 'Begone THOT', 'No', 'ew no', 'GET OUT OF MY SIGHT YOU FILTHY BEGGAR', 'go ask someone ELSE', 'you forgot to say please :p', 'I am NOT A Charity']
money_responses = ['Wow being poor must suck, here take this', 'Here, take some spare change', 'You poor, poor, beggar', 'Oh, I was just looking for someone to give free money to!', 'Take dis mula!', 'Haha I am rich, take this money.', 'Only because you asked nicely :D', 'Sharing is caring!', 'You are very welcome!', 'Idk why I am giving this to you tbh', 'Sure, why not?', 'Fine whatever, just stop bugging me.', 'Sure!']
no_hunt_responses = ['You absolutely **suck** at hunting; No animals for you', 'You went into the forest and somehow manage to catch **nothing** 🤣', "Ur trash at hunting. Nothing for you 😂"]
hunt_responses = ["You go into the forest and hunt a ", "You somehow manage to catch a ", "Wow, it looks like you're not too bad at hunting. **You got a** "]
fish_responses = ["You cast your fishing rod and get a bite!", "You aren't too shabby at fishing!", "Wow you actually managed to catch something noob"]
no_fish_responses = ["You cast your fishing rod but forgot to put on the bait, dumb dumb", "The fish didn't take the bait :(", "Wow you actually **suck** at fishing. No fish for you :p"]



# create a class with what ever name you want.
class ClassName(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    # COMMANDS GO HERE
    # Use @commands instead of @client
    # For events; @commands.Cog.listener()
    @commands.command(name="beg")
    @commands.cooldown(1, 60, BucketType.user)
    async def beg(self, context):
        rand = random.randint(1, 100)
        user_id = context.author.id

        # JACKPOT
        if rand > 99:
            embed_color = discord.Color.dark_green()
            amount = 10000 + random.randint(100, 200)
            desc = f"**Bruh wtf you hit the frickin JACKPOT and got {str(amount)}!!!**"

        # gives user NO money
        elif rand < 31:
            desc = '"' + random.choice(no_money_responses) + '"'
            embed_color = discord.Color.red()
            amount = 0

        # successful (normal) begging
        else:
            response = random.choice(money_responses)
            embed_color = discord.Color.dark_green()
            amount = rand * 10 + random.randint(100, 200)
            desc = '"' + response + '"' + "; **here's: 💰" + str(amount) + '**'
            # add money to bal

        beg_embed = discord.Embed(title=random.choice(random_people), description=desc, color=embed_color)
        beg_embed.set_footer(text="haha u filthy begger")
        await context.reply(embed=beg_embed)
        add_wallet_bal(user_id, amount)

    @commands.command(name="hunt")
    @commands.cooldown(1, 60, BucketType.user)
    async def hunt(self, context):
        user_id = context.author.id

        if get_item_from_inventory(user_id, "bow") == 0:
            await context.reply("You need a bow to go hunting, dummy")
            return

        rand = random.randint(1, 100)

        # counts as a successful hunt
        if rand < 80:
            rarity = random.randint(1, 100)
            # get the rarest item from type "hunting" that is under the random chance
            hunted = get_rarest_item(rarity, "hunting")

            response = random.choice(hunt_responses)

            add_to_inventory(user_id, hunted.get("item_id"))

            await context.send(response + hunted.get("emoji") + ' **' + hunted.get("item_name") + "**")

        else:
            response = random.choice(no_hunt_responses)
            await context.send(response)
            return

    @commands.command(name="fish")
    @commands.cooldown(1, 60, BucketType.user)
    async def fish(self, context):
        user_id = context.author.id

        if get_item_from_inventory(user_id, "fishing pole") == 0:
            await context.reply("You need a fishing pole to go fishing, dummy")
            return

        rand = random.randint(1, 100)

        # counts as a successful hunt
        if rand < 80:
            rarity = random.randint(1, 100)
            # get the rarest item from type "hunting" that is under the random chance
            fished = get_rarest_item(rarity, "fishing")

            response = random.choice(fish_responses)

            add_to_inventory(user_id, fished.get("item_id"))

            await context.send(response + " **You got a** " + fished.get("emoji") + ' **' + fished.get("item_name") + "**")

        else:
            response = random.choice(no_fish_responses)
            await context.send(response)
            return

    @commands.command(name="dig")
    async def dig(self, context):
        user_id = context.author.id

        if get_item_from_inventory(user_id, "pick") == 0:
            await context.reply("You're going to need a pick if you want to dig, pea brain")
            return

        rand = random.randint(1, 100)

        # counts as a successful dig
        if rand > 50:
            if rand > 70:
                random_item_chance = random.randint(0, 100)
                # get a random item from designated types and that is under a random chance
                dug_item = get_rarest_item(random_item_chance, "tool", "mineral")
                item_dig_desc = "and " + dug_item.get("item_name") + " " +dug_item.get("emoji")

            money_dug = rand*7 + random.randint(1, 100)

            desc = "**" + str(money_dug) + "** :moneybag: "

            if 'item_dig_desc' in locals():
                desc += item_dig_desc

            await context.send(f"Wow, you dug up " + desc + ". You lucky duck!")

            add_to_inventory(user_id, dug_item.get("item_id"))
            add_wallet_bal(user_id, money_dug)

        else:
            response = "Oop, you got nothing. Unlucky :p"
            await context.send(response)
            return


# set it up
def setup(client):
    client.add_cog(ClassName(client))
