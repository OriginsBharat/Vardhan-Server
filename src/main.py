import os
import asyncio
import logging
import discord

from bot import MasterBot
from config import Config
from core.ai_services.ollama_client import OllamaClient
from core.ai_services.comfyui_client import ComfyUIClient
from core.ai_services.chatterbox_client import ChatterboxClient
from utils.logging import setup_logging
from core.economic_system.jobs import JobManager

async def main():
    """
    Main entry point for the My AI World application.
    Initializes all services and starts the bot.
    """
    # Setup logging first
    setup_logging()

    try:
        # Load configuration from .env file
        config = Config()

        # Initialize AI Service Clients
        ollama_client = OllamaClient(config.ollama_api_url)
        comfyui_client = ComfyUIClient(config.comfyui_api_url)
        chatterbox_client = ChatterboxClient()

        # Initialize and run the bot
        bot = MasterBot(
            config=config,
            ollama_client=ollama_client,
            comfyui_client=comfyui_client,
            chatterbox_client=chatterbox_client
        )

        # Manually add the job manager after the bot is initialized
        # This resolves a circular dependency where JobManager needs EconomyManager, which is on the bot
        bot.job_manager = JobManager(bot.economy_manager)

        await bot.start(config.discord_bot_token)

    except discord.errors.LoginFailure:
        logging.critical("LOGIN FAILED: The provided DISCORD_BOT_TOKEN is invalid. Please check your .env file or run the setup script.")
    except ValueError as e:
        logging.critical(str(e))
    except Exception as e:
        logging.critical(f"An unexpected error occurred during bot startup: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down the AI World...")
    except Exception as e:
        print(f"A critical error forced the application to stop: {e}")