import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown, MissingRequiredArgument, ChannelNotFound, MemberNotFound
from Helper import verification
import SharedFiles.fb_tokens as fb_tokens

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='+', intents=intents)

# put the name of all the files you want loaded in
initial_extensions = ["verification", "invite"]

# load all the file commands in to this file
if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)

main_embed = discord.Message


@client.command(name="add_reaction")
async def react(context, message_id: discord.Message, *reaction):
    await context.message.delete()
    for i in reaction:
        await message_id.add_reaction(i)


@client.event
async def on_ready():
    # https://discord.gg/RMcwZMqS
    # https://discord.gg/HRDBdUsv
    await client.change_presence(status=discord.Status.online, activity=discord.Game(" +help"))
    channels = client.get_all_channels()
    for channel in channels:
        if str(channel) == "bot-testing":
            bot_channel = client.get_channel(channel.id)
            # await bot_channel.send("Hey, I'm back up!")


@client.event
async def on_message(message):

    await client.process_commands(message)

    if message.author == client.user:
        return()


@client.event
async def on_command_error(ctx, exc):

    if isinstance(exc, CommandOnCooldown):
        time_embed = discord.Embed(title="Command on Cooldown", description="You'll need to wait until \n you can use"
                                                            " this command again!")
        time_embed.add_field(name="Time left", value=f"`{exc.retry_after:,.1f}` seconds")

        await ctx.send(embed=time_embed)

    if isinstance(exc, MissingRequiredArgument):
        await ctx.message.channel.send(f"You forgot to input `{exc.param.name}`!")

    if isinstance(exc, ChannelNotFound):
        await ctx.message.channel.send(f"Channel `{exc.argument}` was not found")

    if isinstance(exc, MemberNotFound):
        await ctx.message.channel.send(f"The following member was not found: `{exc.argument}`")

    raise exc



@client.command(name="embed")
async def embed(context, channel: discord.TextChannel):
    main_embed = await verification.create_verification_embed(context, channel)


# Runs the client on the server
client.run(fb_tokens.get_help_token())
