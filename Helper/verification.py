# create method to be used in another file
import discord
from discord.ext import commands
import SharedFiles.firebase_db as firebase_db
from discord.ext.commands import BucketType
from SharedFiles.firebase_db import add_xp
import SharedFiles.fb_tokens as fb_tokens


# creates verification embed
async def create_verification_embed(context, channel):
    await context.message.delete()

    description = "Hey, welcome to Server Supreme! Our goal  here is for you " \
                  "to have a fun place to talk and meet new people" \
                  ".\n \n You can also earn gold using various commands with" \
                  " our bot(check bot-help) which can be used to purchase" \
                  " moderator privileges(check fief-help). " \
                  "You can also earn gold by inviting friends!\n \n " \
                  "To become verified, click the check!"

    my_embed = discord.Embed(title="Welcome!", description=description, color=0x285394)
    my_embed.set_footer(text='King: 3/5/2021')
    my_embed.set_author(name="📋 King's Advisor")

    message = await channel.send(embed=my_embed)
    await message.add_reaction("🦅")
    await message.add_reaction("🐺")
    await message.add_reaction("🦁")
    await message.add_reaction("🐲")
    return message


# dms user
async def dm_verification_receipt(context, name: discord.Member):
    await context.message.channel.send("ok dude")
    await name.send("hey")


# check if user is already in a fief
def is_in_fief(user_id):
    # check if already stored in fief
    return firebase_db.is_user_in_fief(user_id)


# rewards the inviter
async def reward_inviter(client, inviter_id, member_id):
    if inviter_id == -1:
        return 0

    inviter = client.get_user(inviter_id)
    member = client.get_user(member_id)
    xp = 1000
    money = 1000
    xp_added = add_xp(inviter_id, xp)
    firebase_db.add_wallet_bal(inviter_id, money)
    embed_desc = member.name + " joined and verified with your invite link\n" \
                               "**XP received:** " + str(xp) + "\n" \
                               "**Money received:** :moneybag:" + str(money) + "\n" +\
                               "**Current Level:** " + str(firebase_db.get_level(inviter_id))

    embed = discord.Embed(
        title="Invite Reward",
        description=embed_desc,
        color=discord.Color.green())
    # this will give the inviter xp
    if xp_added == 1:
        await inviter.send(embed=embed)
    elif xp_added == 0:
        await inviter.send(embed=embed)


# add user to a fief
async def add_user_to_fief(client, payload):
    bot_id = fb_tokens.get_bot_id()
    # check if its the bot reacting
    if payload.user_id == bot_id:
        return
    fief_ids = {0: "Aetos Dios", 1: "Fenrir", 2: "Leo Nemeaeus", 3: "Pythoninae"}

    reaction = str(payload.emoji)
    # check what the user reacted with
    if reaction == "🦅":
        fief_id = 0
    elif reaction == "🐺":
        fief_id = 1
    elif reaction == "🦁":
        fief_id = 2
    elif reaction == "🐲":
        fief_id = 3
    else:
        return

    # check if user has already reacted to a fief
    if not is_in_fief(payload.user_id):
        # create user in the database with fief data
        firebase_db.join_fief(payload.user_id, fief_id)
        # once found we add 1 to their num_of_invites
        # maybe only increment once the user becomes verified (needs to choose a fief)
        # this would be done in the verification file add_user_to_fief()
        # add when they get invited?
        inviter_id = firebase_db.get_inviter_id(payload.user_id)
        await reward_inviter(client, inviter_id, payload.user_id)
        firebase_db.increment_num_invites(inviter_id)
        role = discord.utils.get(payload.member.guild.roles, name=fief_ids[fief_id])
        await payload.member.add_roles(role)
        return True
    # user already was assigned a fief
    return False


# create a class with what ever name you want.
class Verify(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # adds user who reacted to fief
        await add_user_to_fief(self.client, payload)

    # COMMANDS GO HERE
    # Use @commands instead of @client
    # for listeners @commands.Cog.listener()


# set it up
def setup(client):
    client.add_cog(Verify(client))

