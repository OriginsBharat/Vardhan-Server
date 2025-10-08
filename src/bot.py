import os
import discord
from discord.ext import commands
from config import Config
from core.ai_services.ollama_client import OllamaClient
from core.ai_services.comfyui_client import ComfyUIClient
from core.ai_services.chatterbox_client import ChatterboxClient
from core.personas import PersonaManager
from core.universe import Universe
from core.economic_system.economy_manager import EconomyManager
from core.world_state.scheduler import Scheduler
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

    async def setup_hook(self):
        """Asynchronous setup hook for the bot."""
        print("Loading extensions...")
        # Load command cogs
        for filename in os.listdir('./src/commands'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'commands.{filename[:-3]}')
                print(f"Loaded command: {filename}")

        # Initialize core systems
        await self.persona_manager.initialize_personas()
        self.scheduler.start()
        print("Core systems initialized.")

    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Set bot presence
        await self.change_presence(activity=discord.Game(name="Watching over my world..."))

        # Check if the server needs to be built
        guild = self.get_guild(self.config.discord_guild_id)
        if guild and len(guild.channels) < 5: # Heuristic for a "blank" server
            print("Server appears to be blank. Initiating World Architect mode...")
            await self.build_server_structure(guild)

    async def build_server_structure(self, guild: discord.Guild):
        """
        Automatically builds the categories and channels for the server.
        """
        print("Building server structure...")

        # Clear existing channels (optional, for a truly clean slate)
        for channel in guild.channels:
            await channel.delete()

        # --- The Citadel (Admin & Control) ---
        citadel_category = await get_or_create_category(guild, "🏰 The Citadel")
        await get_or_create_channel(guild, "announcements", category=citadel_category)
        await get_or_create_channel(guild, "rules-and-lore", category=citadel_category)

        # --- Master's Chambers (Private) ---
        master_role = await guild.create_role(name="Master")
        member = await guild.fetch_member(self.config.user_id)
        if member:
            await member.add_roles(master_role)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            master_role: discord.PermissionOverwrite(read_messages=True)
        }
        master_category = await get_or_create_category(guild, "🔒 Master's Chambers", overwrites=overwrites)
        await get_or_create_channel(guild, "master-control", category=master_category)

        # --- The Market District (Economy) ---
        market_category = await get_or_create_category(guild, "💰 The Market District")
        await get_or_create_channel(guild, "job-board", category=market_category)
        await get_or_create_channel(guild, "the-bazaar", category=market_category) # For bot shops
        await get_or_create_channel(guild, "auction-house", category=market_category)

        # --- The Velvet District (NSFW) ---
        velvet_category = await get_or_create_category(guild, "🔞 The Velvet District")
        await get_or_create_channel(guild, "the-boudoir", category=velvet_category, nsfw=True)
        await get_or_create_channel(guild, "erotica-lounge", category=velvet_category, nsfw=True)

        # --- Public Square (General) ---
        public_category = await get_or_create_category(guild, "🌳 Public Square")
        await get_or_create_channel(guild, "general-chat", category=public_category)
        await get_or_create_channel(guild, "art-gallery", category=public_category)

        print("✅ Server structure built successfully.")