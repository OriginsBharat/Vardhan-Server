# src/bot.py (Minimal version for login test)

import discord
import logging
from src.config import Config

class MasterBot(discord.Client):
    """A minimal bot client to test the Discord login."""
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.config = config

    async def on_ready(self):
        """Called when the bot successfully logs in."""
        logging.info(f"--- SUCCESS! ---")
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logging.info(f"This confirms the bot token is valid and the connection is successful.")
        logging.info(f"I will now shut down to begin the full implementation.")
        await self.close()

    def run_bot(self):
        """Starts the bot using the token from the config."""
        logging.info("Attempting to connect to Discord...")
        try:
            self.run(self.config.DISCORD_BOT_TOKEN)
        except discord.errors.LoginFailure:
            logging.error("CRITICAL: Login failed. The provided DISCORD_BOT_TOKEN is invalid.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during login: {e}")