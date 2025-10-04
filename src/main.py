# src/main.py (Minimal version for login test)

import logging
from src.config import Config
from src.bot import MasterBot
from src.utils.logging import setup_logging

def main():
    """Initializes and runs the minimal bot for the login test."""
    setup_logging()

    try:
        config = Config()
    except ValueError as e:
        logging.error(f"Configuration Error: {e}")
        return

    master_bot = MasterBot(config)
    master_bot.run_bot()

if __name__ == "__main__":
    main()