# src/bot.py
# This file contains the main MasterBot client, the central nervous system of the AI world.

import discord
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from src.config import Config
from src.core.character_system.personas import load_all_personas, Character
from src.core.economic_system.economy_manager import EconomyManager
from src.core.economic_system.job_manager import JobManager
from src.core.economic_system.shop_manager import ShopManager
from src.core.economic_system.auction_house import AuctionHouse
from src.core.event_system.event_ai import EventAI
from src.core.art_system.art_generator import ArtGenerator
from src.core.voice_system.voice_manager import VoiceManager
from src.core.world_state.scheduler import Scheduler
from src.core.world_state.simulation import SimulationManager
from src.commands.control_panel import ControlPanelCommand
from src.utils.discord_utils import send_dm

class MasterBot(discord.Client):
    """
    The main bot client that manages all personas and systems.
    """
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        super().__init__(intents=intents)

        self.config = config
        self.guild: Optional[discord.Guild] = None

        # --- Initialize All Core Systems ---
        self.personas = load_all_personas()
        self.economy_manager = EconomyManager(master_user_id=self.config.USER_ID)
        self.job_manager = JobManager(self.economy_manager)
        self.shop_manager = ShopManager(self.economy_manager)
        self.art_generator = ArtGenerator(self.config)
        self.voice_manager = VoiceManager(self.config)

        self.auction_house = AuctionHouse(self.config, self.economy_manager, self)
        self.event_ai = EventAI(self.config, self)
        self.scheduler = Scheduler(self.personas, self, self.job_manager)
        self.simulation_manager = SimulationManager(self.personas, self.job_manager)

        # --- Initialize Command Handlers ---
        self.control_panel_command = ControlPanelCommand(self.personas)

        logging.info("MasterBot initialized with all subsystems.")

    async def _trial_countdown_loop(self):
        """A background task to check for VPS trial expiration."""
        await self.wait_until_ready()
        while not self.is_closed():
            if self.config.TRIAL_END_DATE:
                try:
                    end_date = datetime.strptime(self.config.TRIAL_END_DATE, "%Y-%m-%d")
                    now = datetime.now()
                    remaining = end_date - now

                    if timedelta(days=0) < remaining <= timedelta(days=3):
                        master_user = self.get_user(self.config.USER_ID)
                        if master_user:
                            logging.info(f"VPS trial ending soon. Notifying Master. Days left: {remaining.days}")
                            await send_dm(master_user, f"**WARNING, MASTER:** Your VPS trial period ends in {remaining.days} day(s) on {self.config.TRIAL_END_DATE}. Please prepare for migration.")
                except ValueError:
                    logging.error("Invalid date format for TRIAL_END_DATE in .env file. Please use YYYY-MM-DD.")
                except Exception as e:
                    logging.error(f"An error occurred in the trial countdown loop: {e}")

            await asyncio.sleep(86400) # Wait 24 hours

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.guild = self.get_guild(self.config.DISCORD_GUILD_ID)
        if not self.guild:
            logging.error(f"CRITICAL: Bot is not a member of the specified guild (ID: {self.config.DISCORD_GUILD_ID}). Shutting down.")
            await self.close()
            return

        logging.info(f'Logged in as {self.user} and connected to guild: {self.guild.name}')

        # Run the offline simulation before starting other loops
        self.simulation_manager.run_offline_simulation()

        # Start all background loops
        self.auction_house.start_loop()
        self.event_ai.start_loop()
        self.scheduler.start_loop()
        self.loop.create_task(self._trial_countdown_loop())

        print("\n--- My AI World v4 is Online ---")
        print(f"Connected to: {self.guild.name}")
        print("All systems running. Awaiting Master's command.")

    async def on_message(self, message: discord.Message):
        if message.author == self.user: return

        # Handle commands from the Master in the designated control channel
        if message.channel.id == self.config.DISCORD_CONTROL_CHANNEL_ID and \
           message.author.id == self.config.USER_ID and \
           message.content.startswith('!'):
            await self.handle_command(message)
            return

    async def handle_command(self, message: discord.Message):
        """Parses and executes commands from the Master."""
        command = message.content.lower().split()[0]

        if command in ["!set", "!status"]:
            await self.control_panel_command.execute(message)
        else:
            await message.channel.send("Unknown command, Master.")

    def run_bot(self):
        try:
            self.run(self.config.DISCORD_BOT_TOKEN)
        except discord.errors.LoginFailure:
            logging.error("CRITICAL: Failed to log in. The provided DISCORD_BOT_TOKEN is invalid.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while running the bot: {e}")

    async def close(self):
        logging.info("Closing all connections...")
        self.simulation_manager.save_shutdown_time()
        self.economy_manager.close()
        await super().close()