import os
import asyncio
from dotenv import load_dotenv
from bot import MasterBot
from config import Config
from core.ai_services.ollama_client import OllamaClient
from core.ai_services.comfyui_client import ComfyUIClient
from core.ai_services.chatterbox_client import ChatterboxClient
from utils.logging import setup_logging

async def main():
    """
    Main entry point for the My AI World application.
    Initializes all services and starts the bot.
    """
    # Load configuration from .env file
    load_dotenv()
    config = Config()

    # Setup logging
    setup_logging()

    # Initialize AI Service Clients
    ollama_client = OllamaClient(config.ollama_api_url)
    comfyui_client = ComfyUIClient(config.comfyui_api_url)
    chatterbox_client = ChatterboxClient(config.chatterbox_url)

    # Initialize and run the bot
    bot = MasterBot(
        config=config,
        ollama_client=ollama_client,
        comfyui_client=comfyui_client,
        chatterbox_client=chatterbox_client
    )

    await bot.start(config.discord_bot_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down the AI World...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")