# src/bot.py
# This file contains the main MasterBot client, the central nervous system of the AI world.

import discord
import logging
import asyncio
import random
import os
from datetime import datetime, timedelta
from typing import List, Optional

from src.config import Config
from src.core.character_system.personas import load_all_personas, Character
from src.core.economic_system.economy_manager import EconomyManager
from src.core.economic_system.jobs import JobManager
from src.core.economic_system.shop import ShopManager
from src.core.economic_system.auction_house import AuctionHouse
from src.core.ai_services.ollama_client import OllamaClient
from src.core.ai_services.chatterbox_client import ChatterboxClient
from src.core.world_state.scheduler import Scheduler
from src.core.world_state.simulation import SimulationManager
from src.commands.control_panel import ControlPanelCommand
from src.utils.discord_utils import send_dm, create_embed

class MasterBot(discord.Client):
    """
    The main bot client that manages all personas and systems.
    """
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.voice_states = True
        super().__init__(intents=intents)

        self.config = config
        self.guild: Optional[discord.Guild] = None

        # --- Initialize All Core Systems ---
        self.personas = load_all_personas()
        self.economy_manager = EconomyManager(master_user_id=self.config.USER_ID)
        self.job_manager = JobManager(self.economy_manager)
        self.shop_manager = ShopManager(self.economy_manager)
        self.ollama_client = OllamaClient(config)
        self.voice_client = ChatterboxClient()
        self.simulation_manager = SimulationManager(self.personas, self.job_manager)

        # --- Initialize Command Handlers ---
        self.control_panel_command = ControlPanelCommand(self.personas)

        logging.info("MasterBot initialized with all subsystems.")

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.guild = self.get_guild(self.config.DISCORD_GUILD_ID)
        if not self.guild:
            logging.error(f"CRITICAL: Bot is not a member of the specified guild (ID: {self.config.DISCORD_GUILD_ID}). Shutting down.")
            await self.close()
            return

        logging.info(f'Logged in as {self.user} and connected to guild: {self.guild.name}')
        self.simulation_manager.run_offline_simulation()

        print("\\n--- My AI World is Online ---")
        print(f"Connected to: {self.guild.name}")
        print("All systems running. Awaiting Master's command.")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.content.startswith('!'):
            if message.author.id == self.config.USER_ID:
                 await self.handle_command(message)
            return

        if self.user.mentioned_in(message) or (random.random() < 0.1):
            responder = random.choice(self.personas)

            prompt = f"You are {responder.name}. Your personality is: {responder.personality_summary}. The user '{message.author.name}' said: '{message.content}'. How do you reply?"

            async with message.channel.typing():
                response_text = await self.ollama_client.get_completion(prompt)

            if response_text:
                embed = create_embed(title=f"{responder.name} says:", description=response_text, color=discord.Color.from_str(responder.aura_color))
                await message.channel.send(embed=embed)

                if message.author.voice and message.author.voice.channel:
                    await self.play_voice_response(responder, response_text, message.author.voice.channel)

    async def play_voice_response(self, character: Character, text: str, voice_channel: discord.VoiceChannel):
        logging.info(f"Attempting to play voice response for {character.name} in {voice_channel.name}")

        speaker_wav_path = f"data/voices/{character.name}.wav"
        if not os.path.exists(speaker_wav_path):
            logging.warning(f"No voice file found for {character.name} at {speaker_wav_path}. Skipping TTS. Please add a voice file to this path.")
            return

        audio_file_path = self.voice_client.generate_speech(text, speaker_wav_path)

        if not audio_file_path:
            logging.error(f"Failed to generate speech audio file for {character.name}.")
            return

        vc = discord.utils.get(self.voice_clients, guild=voice_channel.guild)
        try:
            if vc and vc.is_connected():
                if vc.channel != voice_channel:
                    await vc.move_to(voice_channel)
            else:
                vc = await voice_channel.connect()

            if vc.is_playing():
                vc.stop()

            source = discord.FFmpegPCMAudio(audio_file_path)
            vc.play(source, after=lambda e: logging.error(f'Player error: {e}') if e else None)

            while vc.is_playing():
                await asyncio.sleep(0.5)

            await asyncio.sleep(1)
            await vc.disconnect(force=True)

        except Exception as e:
            logging.error(f"Error playing TTS for {character.name}: {e}")
            if vc and vc.is_connected():
                await vc.disconnect(force=True)
        finally:
            if audio_file_path and os.path.exists(audio_file_path):
                os.remove(audio_file_path)

    async def handle_command(self, message: discord.Message):
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