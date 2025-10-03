import discord, os, asyncio
from dotenv import load_dotenv
from bot_manager import BotManager

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID_STR = os.getenv('DISCORD_GUILD_ID')

if not all([TOKEN, GUILD_ID_STR]):
    print("!!! ERROR: Missing DISCORD_BOT_TOKEN or DISCORD_GUILD_ID in .env file. Please fill it out. !!!")
    exit()

GUILD_ID = int(GUILD_ID_STR)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True # Required for voice functionality

client = discord.Client(intents=intents)
bot_manager = BotManager(client)

@client.event
async def on_ready():
    print(f'>>> {client.user} has connected to Discord!')
    print(">>> Starting background tasks...")
    client.loop.create_task(bot_manager.start_background_tasks())

@client.event
async def on_message(message):
    if message.author.bot or message.webhook_id:
        return
    await bot_manager.handle_message(message)

if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("\n\n!!! LOGIN FAILED: Your DISCORD_BOT_TOKEN in the .env file is incorrect. Please check it and try again. !!!\n\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")