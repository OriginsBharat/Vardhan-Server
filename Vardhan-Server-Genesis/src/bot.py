import discord
from discord.ext import commands
import logging
import random
import os

from config import config
from core.ai_services.ollama_client import OllamaClient
from core.character_system.persona import PersonaManager
from core.economic_system.economy_manager import EconomyManager

class MasterBot(commands.Bot):
    """
    A stable bot for the Crucible Plan, focused on a functional core.
    """
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.logger = logging.getLogger(__name__)
        self.config = config

        self.ollama_client = OllamaClient()
        self.persona_manager = PersonaManager()
        self.economy_manager = EconomyManager(self)

    async def setup_hook(self):
        """Asynchronous setup hook for the bot, called before login."""
        self.logger.info("Loading core command extensions...")
        try:
            # The path is relative to src, where this file is located
            await self.load_extension('commands.control_panel')
            self.logger.info("Loaded command cog: control_panel.py")
        except Exception as e:
            self.logger.error(f"Failed to load the core control_panel cog: {e}", exc_info=True)

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        self.logger.info("The Pantheon is now online and listening.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or message.content.startswith(self.command_prefix):
            return

        mentioned_bots = [p for p in self.persona_manager.get_all_personas() if p.name.lower() in message.content.lower()]
        should_reply_randomly = random.random() < 0.25

        if not mentioned_bots and not should_reply_randomly:
            return

        if mentioned_bots:
            responder_persona = random.choice(mentioned_bots)
        else:
            possible_responders = [p for p in self.persona_manager.get_all_personas() if p.name != message.author.name]
            if not possible_responders: return
            responder_persona = random.choice(possible_responders)

        self.logger.info(f"Interaction triggered: {responder_persona.name} will reply to {message.author.name} in #{message.channel.name}.")

        async with message.channel.typing():
            prompt = f"The user '{message.author.name}' said: '{message.content}'. How do you respond?"

            response = await self.ollama_client.generate_text(
                system_prompt=responder_persona.get_full_prompt(),
                user_prompt=prompt
            )

            if response:
                await message.channel.send(response)
            else:
                self.logger.error(f"Failed to get a valid response for {responder_persona.name}.")
                await message.channel.send(f"*Jules's Note: {responder_persona.name} tried to think, but their mind is blank.*")