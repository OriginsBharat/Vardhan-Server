import asyncio
import logging
import sys
import discord
import os

# When this script is run, its directory ('src') is added to the path.
# So we can import other modules from src directly.
from config import config
from bot import MasterBot

async def main():
    """
    Main entry point for the My AI World application.
    """
    # Configure logging to write to a file in the project root
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'bot.log')

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file, mode='w'), logging.StreamHandler()])

    try:
        logging.info("--- Starting Application ---")
        bot = MasterBot()
        logging.info("The Core is awakening...")
        await bot.start(config.discord_bot_token)
    except (ValueError, discord.errors.LoginFailure) as e:
        logging.critical(f"A critical configuration error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"An unexpected error occurred during bot startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("The world is returning to slumber at the Master's command.")