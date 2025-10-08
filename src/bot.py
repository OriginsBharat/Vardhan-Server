import discord
import asyncio
from pathlib import Path

from src.config import Config
from src.core.personas import PersonaManager
from src.core.universe import Universe
from src.core.economic_system.economy_manager import EconomyManager
from src.core.economic_system.job_manager import JobManager
from src.core.economic_system.shop import ShopManager
from src.core.economic_system.auction_house import AuctionHouse
from src.core.world_state.scheduler import Scheduler
from src.core.world_state.simulation import SimulationManager
from src.core.world_state.event_ai import EventAI
from src.core.ai_services.ollama_client import OllamaClient
from src.core.ai_services.comfyui_client import ComfyUIClient
from src.core.ai_services.chatterbox_client import ChatterboxClient
from src.commands.control_panel import ControlPanel
from src.utils.discord_utils import get_or_create_category, get_or_create_channel

class MasterBot(discord.Client):
    """The main bot class that orchestrates the entire AI world."""
    def __init__(self, config, intents):
        super().__init__(intents=intents)
        self.config = config

        # Core Systems
        self.persona_manager = PersonaManager()
        self.universe = Universe(api_key=config.pinecone_api_key, index_host=config.pinecone_index_host)
        self.economy_manager = EconomyManager()
        self.job_manager = JobManager(self.persona_manager)
        self.shop_manager = ShopManager()
        self.auction_house = AuctionHouse()
        self.scheduler = Scheduler(self)
        self.simulation_manager = SimulationManager(self)
        self.event_ai = EventAI(self)

        # AI Service Clients
        self.llm = OllamaClient(api_url=config.ollama_api_url)
        self.art_generator = ComfyUIClient(server_address=config.comfyui_api_url)
        self.voice_generator = ChatterboxClient()

        # Command Handlers
        self.control_panel = ControlPanel(self)

        # State for Puppet Master feature
        self.master_possessing = False
        self.possessed_character_name = None
        self.channel_cache = {}

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        self.guild = self.get_guild(self.config.guild_id)
        if not self.guild:
            print(f"[FATAL] Guild with ID {self.config.guild_id} not found. The bot cannot operate.")
            await self.close()
            return

        await self.world_architect()
        # self.simulation_manager.run_offline_simulation() # Will be called after channel IDs are set
        # self.loop.create_task(self.scheduler.start())
        # self.loop.create_task(self.event_ai.start())

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Handle Master's possession first
        if self.master_possessing and str(message.author.id) == self.config.user_id:
            if self.possessed_character_name:
                await self.send_as_possessed(message)
            return

        # Handle Master's commands in the control channel
        if self.config.control_channel_id and message.channel.id == self.config.control_channel_id and str(message.author.id) == self.config.user_id:
            if message.content.startswith('!'):
                await self.control_panel.handle_command(message)
                return

    async def send_as_possessed(self, message):
        """Sends a message on behalf of the possessed character."""
        target_channel = self.get_channel(message.channel.id)
        if not target_channel:
            return

        persona = self.persona_manager.get_persona(self.possessed_character_name)
        if not persona:
            return

        # Create a webhook to impersonate the bot
        webhook = await target_channel.create_webhook(name=persona.name)

        # In a multi-bot setup, you'd fetch the bot's real avatar. Here we can't.
        await webhook.send(content=message.content, username=persona.name)
        await webhook.delete()
        await message.delete()

    async def world_architect(self):
        """Builds the entire Discord server structure if it doesn't exist."""
        if discord.utils.get(self.guild.categories, name="🏰 THE CITADEL"):
            print("Server structure already exists. Skipping World Architect.")
            return

        print("First run detected. Building the Discord city of Vardhan...")
        master_member = self.guild.get_member(self.config.user_id)
        if not master_member:
            print("[FATAL] Master user not found in the guild. Cannot create private channels.")
            return

        # Category Creation
        cats = {
            "citadel": await get_or_create_category(self.guild, "🏰 THE CITADEL"),
            "market": await get_or_create_category(self.guild, "💰 THE MARKET DISTRICT"),
            "homes": await get_or_create_category(self.guild, "🏡 CHARACTER HOMES"),
            "velvet": await get_or_create_category(self.guild, "💋 THE VELVET DISTRICT"),
            "arena": await get_or_create_category(self.guild, "⚔️ THE ARENA OF SOULS"),
            "court": await get_or_create_category(self.guild, "⚖️ THE COURTHOUSE"),
            "master": await get_or_create_category(self.guild, "👑 MASTER'S PRIVATE CHAMBERS", is_private=True, target=master_member)
        }

        # Channel Creation
        # Citadel
        await get_or_create_channel(self.guild, "announcements", category=cats['citadel'])
        await get_or_create_channel(self.guild, "general-chat", category=cats['citadel'])
        await get_or_create_channel(self.guild, "art-gallery", category=cats['citadel'])
        await get_or_create_channel(self.guild, "bot-commands", category=cats['citadel'])
        await get_or_create_channel(self.guild, "The Town Square", category=cats['citadel'], type=discord.ChannelType.voice)

        # Market
        await get_or_create_channel(self.guild, "job-board", category=cats['market'])
        await get_or_create_channel(self.guild, "the-bazaar", category=cats['market'])
        await get_or_create_channel(self.guild, "the-auction-house", category=cats['market'])
        await get_or_create_channel(self.guild, "bank-of-vardhan", category=cats['market'])

        # Homes
        for p in self.persona_manager.get_all_personas():
            await get_or_create_channel(self.guild, f"{p.name.lower().replace(' ', '-')}-s-quarters", category=cats['homes'])
        await get_or_create_channel(self.guild, "Living Quarters", category=cats['homes'], type=discord.ChannelType.voice)

        # Velvet District
        await get_or_create_channel(self.guild, "the-scarlet-lounge", category=cats['velvet'], nsfw=True)
        await get_or_create_channel(self.guild, "nsfw-art-gallery", category=cats['velvet'], nsfw=True)
        await get_or_create_channel(self.guild, "The Whispering Suite", category=cats['velvet'], type=discord.ChannelType.voice)
        for i in range(1, 6): # Create 5 private rooms
            await get_or_create_channel(self.guild, f"Private Room {i}", category=cats['velvet'], type=discord.ChannelType.voice)

        # Arena & Courthouse
        await get_or_create_channel(self.guild, "the-coliseum", category=cats['arena'])
        await get_or_create_channel(self.guild, "court-proceedings", category=cats['court'])

        # Master's Chambers
        control_channel = await get_or_create_channel(self.guild, "emotion-control", category=cats['master'])
        await get_or_create_channel(self.guild, "masters-journal", category=cats['master'])
        await get_or_create_channel(self.guild, "event-control", category=cats['master'])

        # This is a critical step: update the live config with the new channel IDs
        self.config.control_channel_id = control_channel.id

        print("World Architect has finished building the city.")
        await control_channel.send(f"Welcome, Master. Your city is built. The world will now come to life.")

        # Now that channels exist, start the main loops
        self.simulation_manager.run_offline_simulation()
        self.loop.create_task(self.scheduler.start())
        self.loop.create_task(self.event_ai.start())