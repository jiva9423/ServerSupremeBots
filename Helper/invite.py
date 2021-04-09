import discord
from discord.ext import commands
import SharedFiles.firebase_db as firebase_db

invites = {}


def find_invite_by_code(invite_list, code):
    # Simply looping through each invite in an
    # invite list which we will get using guild.invites()
    for inv in invite_list:

        # Check if the invite code in this element
        # of the list is the one we're looking for
        if inv.code == code:
            # If it is, we return it.
            return inv


async def create_user_db(user_id):
    if not firebase_db.user_exists(user_id):
        firebase_db.create_user(user_id=user_id, inviter_id=0)
    #await track_invites(member)


# reassign fief role to member who left
async def reassign_fief(member):
    fief_ids = {0: "Aetos Dios", 1: "Fenrir", 2: "Leo Nemeaeus", 3: "Pythoninae"}
    if firebase_db.user_exists(member.id):
        if firebase_db.is_user_in_fief(member.id):
            # re-assign fief
            fief_id = firebase_db.get_user_fief_id(member.id)
            if fief_id == -1:
                return False
            role = discord.utils.get(member.guild.roles, name=fief_ids[fief_id])
            await member.add_roles(role)
            return True
    return False


# keeps track of number of people someone invites
async def track_invites(member):
    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()
    print("We are tracking invites")

    # get the most recent invite link used
    invites[member.guild.id] = await member.guild.invites()
    # Loops for each invite we have for the guild
    # the user joined.

    for invite in invites_before_join:
        # Now, we're using the function we created just
        # before to check which invite count is bigger
        # than it was before the user joined.
        test = find_invite_by_code(invites_after_join, invite.code)
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            # Now that we found which link was used,
            # we will print a couple things in our console:
            # the name, invite code used the the person
            # who created the invite code, or the inviter.

            print(f"Member {member.name} Joined")
            print(f"Invite Code: {invite.code}")
            print(f"Inviter: {invite.inviter}")

            # check if user already exists (if they have been previously invited they will exist)
            if firebase_db.is_user_in_fief(member.id): #EDITED
                print("user already exists")
            else:
                # get the inviter id
                inviter_id = invite.inviter.id
                print(inviter_id)
                # create the user
                firebase_db.create_user(user_id=member.id, inviter_id=inviter_id)

            # We will now update our cache so it's ready
            # for the next user that joins the guild

            invites[member.guild.id] = invites_after_join

            # We return here since we already found which
            # one was used and there is no point in
            # looping when we already got what we wanted
            return


# track invites from a user
class Invite(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        # Getting all the guilds our bot is in
        for guild in self.client.guilds:
            # Adding each guild's invites to our dict
            invites[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # tracks invites that people use
        # create_user_db(member.id)
        #await create_user_db(member.id, member)
        await reassign_fief(member)
        await track_invites(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Updates the cache when a user leaves to make sure
        # everything is up to date
        invites[member.guild.id] = await member.guild.invites()

    # COMMANDS GO HERE
    # Use @commands instead of @client
    # for listeners @commands.Cog.listener()


# set it up
def setup(client):
    client.add_cog(Invite(client))