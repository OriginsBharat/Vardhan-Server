# src/main.py
# Main application entry point for My AI World v4.

import logging
from src.config import Config
from src.bot import MasterBot
from src.utils.logging import setup_logging

def main():
    """
    Initializes all systems and runs the main bot client.
    """
    # Setup logging as the very first step
    setup_logging()

    try:
        # Load configuration from the .env file
        config = Config()
    except ValueError as e:
        # If config is invalid (e.g., missing secrets), log the error and exit.
        logging.error(f"Configuration Error: {e}")
        logging.error("The application cannot start without valid configuration. Please check your .env file.")
        return

    # Initialize the MasterBot, which is the central nervous system for the entire world.
    # It will, in turn, initialize all its subsystems (Economy, Personas, AI services, etc.).
    master_bot = MasterBot(config)

    # Start the bot. This is a blocking call that runs the event loop.
    master_bot.run_bot()

if __name__ == "__main__":
    # This is the entry point of the application.
    main()