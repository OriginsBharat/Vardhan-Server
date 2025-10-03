import discord
import os
import asyncio
from dotenv import load_dotenv
from bot_manager import BotManager

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))

# Set up intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the client and bot manager
client = discord.Client(intents=intents)
bot_manager = BotManager(client)

@client.event
async def on_ready():
    """Event handler for when the bot connects to Discord."""
    print(f'{client.user} has connected to Discord!')
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print(f"Error: Guild with ID {GUILD_ID} not found.")
        return

    print(f"Connected to guild: {guild.name} (id: {guild.id})")
    print("Bot is ready and listening for messages.")

    # Start the autonomous conversation loop as a background task
    client.loop.create_task(bot_manager.start_conversation_loop())

@client.event
async def on_message(message):
    """Event handler for when a message is sent."""
    # Don't let the bot respond to its own messages
    # This will be more complex later when bots have their own client instances
    if message.author == client.user:
        return

    # Pass the message to the bot manager to handle
    await bot_manager.handle_message(message)

if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Bot token not found. Please follow the instructions in the setup guide.")
    else:
        try:
            client.run(TOKEN)
        except discord.errors.LoginFailure:
            print("Failed to log in. Please ensure your DISCORD_BOT_TOKEN is correct.")
        except Exception as e:
            print(f"An error occurred: {e}")