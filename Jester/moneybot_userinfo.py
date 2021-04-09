# create method to be used in another file
import discord
from discord.ext import commands
from datetime import date
from SharedFiles.firebase_db import get_wallet_bal, get_bank_bal, get_bank_space, add_bank_bal, sub_bank_bal, sub_wallet_bal, deposit_to_bank, withdraw_from_bank, add_wallet_bal

today = date.today()


# checks to see if given string is number
def is_number(number):
    # tries to convert string to float
    try:
        int(number)
        # if successful, return true
        return True
    # if ValueError, return false
    except ValueError:
        return False


# create a class with what ever name you want.
class ClassName(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client

    # COMMANDS GO HERE
    # Use @commands instead of @client
    # For events; @commands.Cog.listener()
    @commands.command(name="balance", aliases=["bal", "money"])
    async def bal(self, context, user: discord.Member = None):
        if not user:
            user = context.author
            user_id = context.author.id
            name = user.display_name
        else:
            user_id = user.id
            name = user.display_name

        wallet_bal = f'{int(get_wallet_bal(user_id)):,}'
        bank_bal = f'{int(get_bank_bal(user_id)):,}'
        bank_space = f'{int(get_bank_space(user_id)):,}'

        bal_embed = discord.Embed(title=f"{name}'s Balance", description=f"**Wallet Balance:**\n💰{wallet_bal}\n**Bank Balance:**\n 💰{bank_bal}/{bank_space}", color=discord.Color.dark_orange())
        bal_embed.set_footer(text=today.strftime("%B %d, %Y"))
        await context.send(embed=bal_embed)

    @commands.command(name="deposit", aliases=["dep", "put"])
    async def deposit(self, context, amount):

        if not amount:
            await context.reply("You have to give an amount you dummy")
            return

        user_id = context.author.id
        wallet_bal = get_wallet_bal(user_id)
        bank_bal = get_bank_bal(user_id)
        bank_space = get_bank_space(user_id)

        if amount == "all":
            deposit_amount = wallet_bal
        elif amount == "half":
            deposit_amount = round(int(wallet_bal/2))
        elif not is_number(amount):
            await context.reply("You have to give a number you dumb dumb")
            return()
        elif is_number(amount):
            deposit_amount = int(amount)

        bank_left = bank_space - bank_bal

        if bank_left == 0:
            await context.reply("You don't have any space left in your bank you dolt")
            return

        if deposit_amount > bank_space:
            deposit_amount = bank_left

        if deposit_amount < 1:
            await context.reply("You can't deposit negative money noob")
            return

        await context.reply("You have succesfully deposited 💰**" + str(deposit_amount) + "**!")

        deposit_to_bank(user_id, deposit_amount)

    @commands.command(name="withdraw", aliases=["with", "take"])
    async def withdraw(self, context, amount):

        if not amount:
            await context.reply("You have to give an amount you dummy")
            return

        user_id = context.author.id
        bank_bal = get_bank_bal(user_id)

        if amount == "all":
            withdraw_amount = bank_bal
        elif amount == "half":
            withdraw_amount = round(int(bank_bal / 2))
        elif not is_number(amount):
            await context.reply("You have to give an amount you dumb dumb!")
            return
        elif is_number(amount):
            withdraw_amount = int(amount)

        if withdraw_amount < 1:
            await context.reply("You can't withdraw that. Don't try to break me noob")
            return

        if bank_bal < 1:
            await context.reply("You don't have any money left in your bank you dolt!")
            return

        if withdraw_amount > bank_bal:
            await context.reply("You don't have that much money, stoopid")
            return

        await context.reply("You have succesfully withdrawn 💰**" + str(withdraw_amount) + "**!")

        withdraw_from_bank(user_id, withdraw_amount)


    @commands.command(name="coolpersongib", hidden=True)
    async def admingive(self, context, user_id: int, amount: int, bank_or_wallet):
        admin_ids = [719989279505252414, 553627849232220160]
        if context.author.id not in admin_ids:
            return
        if bank_or_wallet == "wallet":
            if amount < 1:
                sub_wallet_bal(user_id, amount*-1)
            add_wallet_bal(user_id, amount)
            await context.message.delete()
        if bank_or_wallet == "bank":
            if amount < 1:
                sub_bank_bal(user_id, amount*-1)
            add_bank_bal(user_id, amount)
        await context.message.delete()


# set it up
def setup(client):
    client.add_cog(ClassName(client))
