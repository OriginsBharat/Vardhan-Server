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
from core.world_state.justice import JusticeManager
from core.world_state.narrative_manager import NarrativeManager
from core.world_state.narrative_manager import NarrativeManager
from core.economic_system.loan_manager import LoanManager
from core.economic_system.black_market_manager import BlackMarketManager
from core.character_system.scar_manager import ScarManager
from core.world_state.arena_manager import ArenaManager
from core.world_state.interaction_manager import InteractionManager
from core.economic_system.contract_manager import ContractManager
from core.world_state.autonomous_actions import AutonomousActionManager
from core.world_state.event_ai import EventAI
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

        # Order is important here. Managers that depend on others should be initialized after their dependencies.
        self.persona_manager = PersonaManager(self)
        self.universe = Universe(config)
        self.economy_manager = EconomyManager()
        self.scheduler = Scheduler(self)
        self.simulation_manager = SimulationManager(self)
        self.justice_manager = JusticeManager(self)
        self.loan_manager = LoanManager(self)
        self.narrative_manager = NarrativeManager(self)
        self.scar_manager = ScarManager(self)
        self.black_market_manager = BlackMarketManager(self)
        self.arena_manager = ArenaManager(self)
        self.interaction_manager = InteractionManager(self)
        self.contract_manager = ContractManager(self)
        self.autonomous_action_manager = AutonomousActionManager(self)
        self.event_ai = EventAI(self)
        self.job_manager = None # Will be initialized in main.py
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self):
        """Asynchronous setup hook for the bot."""
        self.logger.info("Loading extensions...")
        commands_dir = os.path.join(os.path.dirname(__file__), 'commands')
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    # Corrected path for loading extensions from the 'src' directory
                    await self.load_extension(f'src.commands.{filename[:-3]}')
                    self.logger.info(f"Loaded command extension: {filename}")
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

        # Check if the server is empty (less than 5 channels is a good heuristic)
        if len(guild.channels) < 5:
            self.logger.info("Server appears to be blank. Initiating World Architect mode...")
            await self.build_server_structure(guild)

        # Run the offline simulation after the bot is fully ready
        await self.simulation_manager.run_offline_simulation()

        await self.change_presence(activity=discord.Game(name="Watching over my world..."))
        self.logger.info("Bot is ready and online.")

    async def on_message(self, message: discord.Message):
        """Primary message handler for the bot."""
        # Ignore messages from bots (including self) to prevent loops
        if message.author.bot:
            return

        # Check if the Master is possessing a bot
        control_panel_cog = self.get_cog("Control Panel")
        if control_panel_cog and control_panel_cog.possessed_bot_persona and message.author.id == self.config.user_id:
            await control_panel_cog.handle_possession(message)
            return  # Stop further processing to avoid command execution

        # Check if the bot was mentioned
        if self.user.mentioned_in(message):
            # For now, let's have Maya respond to all direct mentions
            # A more advanced system could determine which bot is "active" in the channel
            persona = self.persona_manager.get_persona("Maya")
            if persona:
                async with message.channel.typing():
                    await self.respond_to_mention(message, persona)

        # Always process commands at the end
        await self.process_commands(message)

    async def respond_to_mention(self, message: discord.Message, persona):
        """Generates and sends a formatted response to a mention."""
        from utils.formatting import enforce_action_text_format

        self.logger.info(f"Generating response for {persona.name} to a mention from {message.author.display_name}")

        # A more advanced implementation would fetch conversation history from the Universe
        recent_history = f"The Master, {message.author.display_name}, said to you: '{message.clean_content}'"

        prompt = (
            f"{persona.get_full_prompt()}\n\n"
            "This is the current situation:\n"
            f"{recent_history}\n\n"
            "Based on this, what is your immediate response? Remember to use the *action* text *action* format."
        )

        response_text = await self.ollama_client.generate_text(prompt, self.config.llm_model)

        if "Error:" not in response_text and response_text:
            # Enforce the formatting utility here
            formatted_response = enforce_action_text_format(response_text)
            await message.channel.send(formatted_response)
            self.narrative_manager.log_event(f"{persona.name} had a conversation with the Master in #{message.channel.name}.")
        else:
            self.logger.error(f"Failed to generate a response for {persona.name}: {response_text}")
            await message.channel.send(f"*{persona.name} seems lost in thought and doesn't respond.*")

    async def build_server_structure(self, guild: discord.Guild):
        """
        Automatically builds the categories and channels for the server based on the blueprint.
        """
        self.logger.info("Executing World Architect to build server structure...")

        # Clear existing channels to start fresh
        for channel in guild.channels:
            await channel.delete()

        # --- Create Roles ---
        master_role, _ = await self._get_or_create_role(guild, "Master")
        member = await guild.fetch_member(self.config.user_id)
        if member:
            await member.add_roles(master_role)

        # --- Define Overwrites ---
        master_only_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            master_role: discord.PermissionOverwrite(read_messages=True)
        }

        # --- Create Categories and Channels ---
        # THE CITADEL
        citadel_cat = await get_or_create_category(guild, "🏰 THE CITADEL")
        await get_or_create_channel(guild, "announcements", category=citadel_cat)
        await get_or_create_channel(guild, "rules-and-lore", category=citadel_cat)
        await get_or_create_channel(guild, "general-chat", category=citadel_cat)
        await get_or_create_channel(guild, "sfw-art-gallery", category=citadel_cat)
        await get_or_create_channel(guild, "bot-commands-list", category=citadel_cat)
        await guild.create_voice_channel("🔊 The Town Square", category=citadel_cat)

        # THE MARKET DISTRICT
        market_cat = await get_or_create_category(guild, "💰 THE MARKET DISTRICT")
        await get_or_create_channel(guild, "job-board", category=market_cat)
        await get_or_create_channel(guild, "the-bazaar", category=market_cat)
        await get_or_create_channel(guild, "the-auction-house", category=market_cat)
        await get_or_create_channel(guild, "bank-of-vardhan", category=market_cat)
        # Create the hidden black market channel, visible only to the Master initially.
        await get_or_create_channel(guild, "the-black-market", category=market_cat, overwrites=master_only_overwrites)
        await guild.create_voice_channel("🔊 The Trading Floor", category=market_cat)

        # CHARACTER HOMES
        homes_cat = await get_or_create_category(guild, "🏡 CHARACTER HOMES")
        for persona_name in self.persona_manager.personas.keys():
            channel_name = f"{persona_name.lower().replace(' ', '-')}-s-quarters"
            await get_or_create_channel(guild, channel_name, category=homes_cat, nsfw=True)
        await guild.create_voice_channel("🔊 The Living Quarters", category=homes_cat)

        # THE VELVET DISTRICT
        velvet_cat = await get_or_create_category(guild, "💋 THE VELVET DISTRICT")
        await get_or_create_channel(guild, "the-scarlet-lounge", category=velvet_cat, nsfw=True)
        await get_or_create_channel(guild, "nsfw-art-gallery", category=velvet_cat, nsfw=True)
        await get_or_create_channel(guild, "erotica-lounge", category=velvet_cat, nsfw=True)
        await guild.create_voice_channel("🔊 The Whispering Suite", category=velvet_cat)
        for i in range(1, 4):
            await guild.create_voice_channel(f"🔊 Private Room {i}", category=velvet_cat)

        # THE HALL OF JUDGEMENT
        judgment_cat = await get_or_create_category(guild, "⚖️ THE HALL OF JUDGEMENT")
        await get_or_create_channel(guild, "the-courthouse", category=judgment_cat)
        await get_or_create_channel(guild, "the-jail", category=judgment_cat)
        await guild.create_voice_channel("🔊 The Deliberation Chamber", category=judgment_cat)

        # THE ARENA OF SOULS
        arena_cat = await get_or_create_category(guild, "⚔️ THE ARENA OF SOULS")
        await get_or_create_channel(guild, "the-coliseum", category=arena_cat)
        await guild.create_voice_channel("🔊 The Spectator Stands", category=arena_cat)

        # MASTER'S PRIVATE CHAMBERS
        master_cat = await get_or_create_category(guild, "👑 MASTER'S PRIVATE CHAMBERS", overwrites=master_only_overwrites)
        await get_or_create_channel(guild, "emotion-control", category=master_cat)
        await get_or_create_channel(guild, "masters-journal", category=master_cat)
        await get_or_create_channel(guild, "event-control", category=master_cat)

        self.logger.info("✅ Server structure built successfully.")

    async def _get_or_create_role(self, guild: discord.Guild, role_name: str):
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            self.logger.info(f"Creating new role: {role_name}")
            role = await guild.create_role(name=role_name)
        return role, True