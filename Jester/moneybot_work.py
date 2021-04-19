# create method to be used in another file
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import random
from SharedFiles.firebase_db import add_wallet_bal, add_to_inventory, get_an_item, get_items_by_type, get_rarest_item

random_people = ["Random Stranger", "Your mom", "Your dad", "The King", "The Baron", "A Knight in Shining Armor", "Marco Polo", "That one dude", "Genghis Khan", "King Arthur", "Vlad the Impaler", "Leonardo DaVinci", "Some guy from the future", "Baker", "A horse", "Your mom's bf", "John", "John Cena", "A wild pokemon!", "That guy on the wanted posters", "Mr. Beast", "John", "Bob", "Bobalina", "Margaret"]
no_money_responses = ['Haha, imagine begging', 'My mommy told me not to give money to strangers', '*stares at you awkwardly*', 'Here you can have this: *nothing*.', 'Haha. No', 'Go away filthy beggar', 'Begone THOT', 'No', 'ew no', 'GET OUT OF MY SIGHT YOU FILTHY BEGGAR', 'go ask someone ELSE', 'you forgot to say please :p', 'I am NOT A Charity']
money_responses = ['Wow being poor must suck, here take this', 'Here, take some spare change', 'You poor, poor, beggar', 'Oh, I was just looking for someone to give free money to!', 'Take dis mula!', 'Haha I am rich, take this money.', 'Only because you asked nicely :D', 'Sharing is caring!', 'You are very welcome!', 'Idk why I am giving this to you tbh', 'Sure, why not?', 'Fine whatever, just stop bugging me.', 'Sure!']
no_hunt_responses = ['You absolutely **suck** at hunting; No animals for you', 'You go into the forest and somehow manage to catch **nothing** 🤣', "You are trash at hunting tbh. Nothing for you 😂"]
hunt_responses = ["You go into the forest and hunt a ", "You somehow manage to catch ", "Wow, it looks like you're not too bad at hunting. *You got a* "]




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
    async def hunt(self, context):
        rand = random.randint(1, 100)

        # counts as a successful hunt
        if rand < 80:

            # get the rarest item from type "hunting" that is under the random chance
            hunted = get_rarest_item(rand, "hunting")

            response = random.choice(hunt_responses)

            random_addition = random.choice([' *wtf?*', " 😲", ' * all luck no skill, noob*', ' 😱'])

            add_to_inventory(context.author.id, hunted.get("item_id"))

            await context.send(response + hunted.get("emoji") + ' ' + hunted.get("item_name") + random_addition)

        else:
            response = random.choice(no_hunt_responses)
            await context.send(response)
            return


# set it up
def setup(client):
    client.add_cog(ClassName(client))
