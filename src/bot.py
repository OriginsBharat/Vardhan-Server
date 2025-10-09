import os
import discord
from discord.ext import commands
import logging

from config import Config
from core.ai_services.ollama_client import OllamaClient
from core.ai_services.comfyui_client import ComfyUIClient
from core.ai_services.chatterbox_client import ChatterboxClient
from core.character_system.personas import PersonaManager
from core.character_system.universe import Universe
from core.economic_system.economy_manager import EconomyManager
from core.world_state.scheduler import Scheduler
from core.world_state.simulation import SimulationManager
from utils.discord_utils import get_or_create_category, get_or_create_channel

class MasterBot(commands.Bot):
    """
    The main bot class that orchestrates the entire AI World.
    """
    def __init__(self, config: Config, ollama_client: OllamaClient, comfyui_client: ComfyUIClient, chatterbox_client: ChatterboxClient):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

        self.config = config
        self.ollama_client = ollama_client
        self.comfyui_client = comfyui_client
        self.chatterbox_client = chatterbox_client

        self.persona_manager = PersonaManager(self)
        self.universe = Universe(config)
        self.economy_manager = EconomyManager()
        self.scheduler = Scheduler(self)
        self.simulation_manager = SimulationManager(self)
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self):
        """Asynchronous setup hook for the bot."""
        self.logger.info("Loading extensions...")
        for filename in os.listdir('./src/commands'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'commands.{filename[:-3]}')
                    self.logger.info(f"Loaded command: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to load command {filename}: {e}")

        await self.persona_manager.initialize_personas()
        self.scheduler.start()
        self.logger.info("Core systems initialized.")

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.logger.info(f'Logged in as {self.user} (ID: {self.user.id})')

        guild = self.get_guild(self.config.discord_guild_id)
        if not guild:
            self.logger.critical(f"Cannot find the GUILD with ID: {self.config.discord_guild_id}. Please check your .env file.")
            await self.close()
            return

        if len(guild.channels) < 5:
            self.logger.info("Server appears to be blank. Initiating World Architect mode...")
            await self.build_server_structure(guild)

        await self.simulation_manager.run_offline_simulation()

        await self.change_presence(activity=discord.Game(name="Watching over my world..."))
        self.logger.info("Bot is ready and online.")

    async def build_server_structure(self, guild: discord.Guild):
        """
        Automatically builds the categories and channels for the server.
        """
        self.logger.info("Building server structure...")

        for channel in guild.channels:
            await channel.delete()

        citadel_category = await get_or_create_category(guild, "🏰 The Citadel")
        await get_or_create_channel(guild, "announcements", category=citadel_category)
        await get_or_create_channel(guild, "rules-and-lore", category=citadel_category)

        master_role, _ = await self._get_or_create_role(guild, "Master")
        member = await guild.fetch_member(self.config.user_id)
        if member:
            await member.add_roles(master_role)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            master_role: discord.PermissionOverwrite(read_messages=True)
        }
        master_category = await get_or_create_category(guild, "🔒 Master's Chambers", overwrites=overwrites)
        await get_or_create_channel(guild, "master-control", category=master_category)

        market_category = await get_or_create_category(guild, "💰 The Market District")
        await get_or_create_channel(guild, "job-board", category=market_category)
        await get_or_create_channel(guild, "the-bazaar", category=market_category)
        await get_or_create_channel(guild, "auction-house", category=market_category)

        velvet_category = await get_or_create_category(guild, "🔞 The Velvet District")
        await get_or_create_channel(guild, "the-boudoir", category=velvet_category, nsfw=True)
        await get_or_create_channel(guild, "erotica-lounge", category=velvet_category, nsfw=True)

        public_category = await get_or_create_category(guild, "🌳 Public Square")
        await get_or_create_channel(guild, "general-chat", category=public_category)
        await get_or_create_channel(guild, "art-gallery", category=public_category)

        self.logger.info("✅ Server structure built successfully.")

    async def _get_or_create_role(self, guild: discord.Guild, role_name: str):
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            self.logger.info(f"Creating new role: {role_name}")
            role = await guild.create_role(name=role_name)
        return role, True