import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown, MissingRequiredArgument, ChannelNotFound, MemberNotFound, BucketType
import random
import SharedFiles.fb_tokens as fb_tokens
import SharedFiles.firebase_db as firebase
import asyncio

users_on_cooldown = []

cooldown_titles = ["Chillax my guy", "What's the hurry?", "Take a chill pill", "Slow down a bit", "Slow it down a notch", "Spam ain't cool"]

beg_description = ["Slow down on the begging you lowly BEGGAR", "Don't spam da beg"]


client = commands.Bot(command_prefix="!", case_insensitive=True)


# put the name of all the files you want loaded in
initial_extensions = ["moneybot_work", "moneybot_userinfo", "moneybot_gambling", "item_commands", "xp_management", "inventory_commands"]

# load all the file commands in to this file
if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)


@client.event
async def on_ready():
    firebase.init()
    firebase.all_data = firebase.get_all_data()
    print("reeady")
    #print(firebase.all_data)


@client.event
async def on_command_error(ctx, exc):

    message = ctx.message.content

    args = message.split()

    command_invoked = args[0].replace("!", "")

    if isinstance(exc, CommandOnCooldown):

        if command_invoked == "beg":
            command_desc = random.choice(beg_description) + ". You can get\n more coins in"

        time_embed = discord.Embed(title=random.choice(cooldown_titles), description=f"{command_desc} **{exc.retry_after:,.0f} seconds** \n *The default cooldown is `{exc.cooldown.per:,.0f}` seconds but you can\n lower it by leveling up!*", color=discord.Color.dark_blue())
        #time_embed.add_field(name="Time left", value=f"`{exc.retry_after:,.1f}` seconds")

        await ctx.send(embed=time_embed)

    if isinstance(exc, MissingRequiredArgument):
        await ctx.message.channel.send(f"You forgot to input `{exc.param.name}` you dummy!")

    if isinstance(exc, MemberNotFound):
        await ctx.message.channel.send(f"`{exc.argument}` isn't even a member you doofus")

    raise exc


@client.event
async def on_message(message):

    await client.process_commands(message)

    if message.author == client.user:
        return


client.run(fb_tokens.get_d_token())

