# create method to be used in another file
from discord.ext import commands
import asyncio
from SharedFiles.firebase_db import add_xp, get_level
import random

users_on_cooldown = []


async def on_message_xp_add(message):
    user = message.author.id
    if user in users_on_cooldown:
        return

    if user not in users_on_cooldown:
        xp_amount = random.randint(30, 70)
        # leveled up
        if add_xp(user, xp_amount) == 1:
            await message.channel.send(f"{message.author.mention} leveled up! **New level:{get_level(user)}**")
        users_on_cooldown.append(user)

        # cooldown
        await asyncio.sleep(60)
        users_on_cooldown.remove(user)


# create a class with what ever name you want.
class ClassName(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client


    # COMMANDS GO HERE
    # Use @commands instead of @client
    # For events; @commands.Cog.listener()
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.client.user:
            return

        await on_message_xp_add(message)


# set it up
def setup(client):
    client.add_cog(ClassName(client))