import discord
import asyncio
from src.config import Config
from src.bot import MasterBot

def main():
    """The main entry point for the AI World."""
    try:
        config = Config()
    except ValueError as e:
        print(f"[FATAL] Configuration error: {e}")
        print("Please ensure your .env file is correctly set up.")
        return

    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    intents.members = True

    bot = MasterBot(config=config, intents=intents)

    try:
        bot.run(config.discord_bot_token)
    except discord.LoginFailure:
        print("[FATAL] Failed to log in. The provided DISCORD_BOT_TOKEN is invalid.")
    except Exception as e:
        print(f"[FATAL] An unexpected error occurred while running the bot: {e}")

if __name__ == "__main__":
    main()