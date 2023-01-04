#vote-checking-bot
import os
import discord
import botVoteData as data
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
client = discord.Client(intents=intents)
channel = ""
reaction = "\u267B"

@client.event
async def on_ready():
    print(f'connected as {discord.user}')
    await update_attendance()

# Utility function that returns the attendance channel
def get_channel():
    channels = client.get_all_channels() 
    for chnl in channels:
        if chnl.name == "attendance":
            channel_id = chnl.id
            break
    channel = client.get_channel(channel_id)
    return channel

# Utility function that returns the first message in the attendance channel
async def get_message():
    channel = get_channel()
    messages = await channel.history(oldest_first=True).flatten()
    if len(messages)>0:
        first = messages[0]
        await channel.send("...Wait out.")
        for message in messages[1:]:
            await message.delete()
        return first
    else:
        await channel.send("...Wait out.")
        return await get_message()

# Render the attendance image and provide a reaction to update
async def update_attendance():
    data.render_attendance()
    image = discord.File("attendance.png")
    #Delete the first message (old attendance information)
    first = await get_message()
    await first.delete()
    #Send updated information in its place
    await get_channel().send(file=image)
    message = await get_message()
    await message.add_reaction(reaction)

# Regenerate the attendance once a reaction is pressed.
@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        await update_attendance()

client.run(TOKEN)