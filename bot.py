import os
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@client.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    Prints a message indicating that the bot is online and syncs the bot's commands.
    """
    print(f'{client.user} is now online.')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as error:
        print(f"Failed to sync commands: {error}")

async def load():
    """
    A function that loads extensions from each Python file in the './cogs' directory.
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    """
    Asynchronous function that initializes the client, loads extensions, and starts the client.
    """
    async with client:
        await load()
        await client.start(os.environ.get('DISCORD_KEY'))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Exiting...")
