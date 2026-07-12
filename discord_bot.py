import os
import discord
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

sessions: dict[str, list] = {}   # channel_id/user_id -> conversation history


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    session_id = str(message.channel.id)
    history    = sessions.get(session_id, [])

    async with message.channel.typing():
        reply, updated_history = run_agent(message.content, history)
        sessions[session_id] = updated_history

    # Discord has a 2000 character limit per message
    for chunk in [reply[i:i+1900] for i in range(0, len(reply), 1900)]:
        await message.channel.send(chunk)


client.run(DISCORD_TOKEN)