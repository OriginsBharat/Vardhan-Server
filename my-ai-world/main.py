import discord
import os
import asyncio
from dotenv import load_dotenv
from bot_manager import BotManager

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID_STR = os.getenv('DISCORD_GUILD_ID')

# Basic validation to ensure essential variables are set
if not all([TOKEN, GUILD_ID_STR]) or "YOUR_DISCORD_BOT_TOKEN_HERE" in TOKEN:
    print("!!! FATAL ERROR: 'DISCORD_BOT_TOKEN' or 'DISCORD_GUILD_ID' not found or not set in .env file.")
    print("!!! Please fill out the .env file before running the bot. !!!")
    exit()

GUILD_ID = int(GUILD_ID_STR)

# Set up Discord intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True # Required for voice functionality

# Initialize the Discord client and the BotManager
client = discord.Client(intents=intents)
bot_manager = BotManager(client)

@client.event
async def on_ready():
    """Event handler for when the bot successfully connects to Discord."""
    print(f'>>> {client.user} has connected to Discord!')
    print(">>> Initializing Bot Manager and background tasks...")
    # Start the main background loop
    client.loop.create_task(bot_manager.start_background_tasks())

@client.event
async def on_message(message):
    """Event handler for when a message is sent in a channel the bot can see."""
    # Ignore messages from bots (including self) and webhooks to prevent loops
    if message.author.bot or message.webhook_id:
        return

    # Pass the message to the BotManager for handling
    await bot_manager.handle_message(message)

if __name__ == "__main__":
    print(">>> Starting AI World bot...")
    client.run(TOKEN)