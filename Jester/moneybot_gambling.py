# create method to be used in another file
import discord
from discord.ext import commands
import random
import asyncio
from SharedFiles.firebase_db import add_wallet_bal, sub_wallet_bal, get_wallet_bal

coin_images = ['https://imgur.com/qTOevzI', 'https://imgur.com/VW30zVh', 'https://imgur.com/ybM3uDY', 'https://imgur.com/zUrl17g', 'https://imgur.com/sQbcFl4', 'https://imgur.com/20vY6HE', 'https://imgur.com/JdTz4mq', 'https://imgur.com/oMkRmV2']
# create a class with what ever name you want.


class ClassName(commands.Cog):

    # initialize it
    def __init__(self, client):
        self.client = client


    # COMMANDS GO HERE
    # Use @commands instead of @client
    # For events; @commands.Cog.listener()
    @commands.command(name="cointoss", aliases=["cf", "flip", "toss", "coinflip"])
    async def cointoss(self, context, amount):

        def check(msg):
            return msg.author == context.author and msg.channel == context.channel

        sides = ["heads", "tails"]

        user_id = context.author.id

        player_bal = get_wallet_bal(user_id)

        if amount == "all":
            amount = player_bal

        amount = int(amount)

        if amount > player_bal or amount < 1:
            await context.reply("You have to give a wager more that's more than 0 and isn't more than your current wallet balance, noob")
            return

        try:
            await context.send("*Flick.* You have five seconds to respond with a side before the :coin:  hits the ground! ")
            side = await self.client.wait_for("message", check=check, timeout=5)
            side_content = side.content
            if side_content not in sides:
                await side.reply("You have to choose a valid side, dumb dumb. You lose your bet for being so dumb :pensive:")
                sub_wallet_bal(user_id, amount)
                return

        except asyncio.TimeoutError:
            await context.reply(f"You didn't call a side in time, you slow poke. *You lost your entire bet* (💰{amount})")
            sub_wallet_bal(user_id, amount)

        rand_side = random.choice(sides)
        user_id = context.author.id

        # loss
        if side.lower() not in rand_side:
            desc = f"**You lose**\n The coin landed on **{rand_side}** and you chose **{side}**\n Better luck next time! You lost **💰{str(amount)}**"
            lose_embed = discord.Embed(title=f"**You lose**", color=discord.Color.red(), description=desc)
            lose_embed.set_author(name=f"{context.author.display_name}'s Cointoss", icon_url=context.author.avatar_url)
            await context.reply(embed=lose_embed)
            sub_wallet_bal(user_id, amount)
        # win
        else:
            desc = f"**You Win**\n It landed on {rand_side} and you chose {side}\n Congrats! You win 💰**{str(amount)}**"
            win_embed = discord.Embed(title=f"**You win**", color=discord.Color.green(), description=desc)
            win_embed.set_author(name=f"{context.author.display_name}'s Cointoss", icon_url=context.author.avatar_url)
            await context.reply(embed=win_embed)
            add_wallet_bal(user_id, amount)

# set it up
def setup(client):
    client.add_cog(ClassName(client))