import logging
import random
from core.character_system.personas import Persona

class EventAI:
    """
    The Director of the world, responsible for creating autonomous world events
    and psychologically targeting individual bots.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def consider_whispers_of_madness(self):
        """
        Periodically selects a random bot and attempts to erode their sanity.
        """
        # This action should be rare to be impactful
        if random.random() > 0.1: # 10% chance per check
            return

        # Select a random target that is not Maya
        targetable_personas = [p for p in self.bot.persona_manager.personas.values() if p.name != "Maya"]
        if not targetable_personas:
            return

        target_persona = random.choice(targetable_personas)

        self.logger.info(f"Director AI is targeting {target_persona.name} with Whispers of Madness.")

        # The whisper itself is a narrative event, and it reduces sanity
        sanity_damage = random.randint(5, 15)
        target_persona.emotions['sanity'] = max(0, target_persona.emotions.get('sanity', 100) - sanity_damage)

        # Generate a prompt for the whisper
        prompt = (
            f"You are the Director, a god-like entity of this world. "
            f"You are subtly tormenting {target_persona.name}. "
            f"Describe a brief, unsettling, paranoid, or maddening event that only they experience. "
            f"It could be a fleeting shadow, a misplaced object, a voice on the wind, or a distorted reflection. "
            f"Keep it short and unnerving."
        )

        whisper_text = await self.bot.ollama_client.generate_text(prompt, self.bot.config.llm_model)

        if "Error:" not in whisper_text and whisper_text:
            # Log this event for the Master's Journal
            full_event_text = (
                f"The Director AI inflicted a 'Whisper of Madness' upon {target_persona.name}, "
                f"causing their sanity to drop. They experienced the following: {whisper_text}"
            )
            self.bot.narrative_manager.log_event(full_event_text, level="critical")

            # Announce it subtly in a public channel
            channel = self.bot.get_channel(self.bot.config.discord_guild_id) # This needs a specific channel
            general_channel = discord.utils.get(self.bot.get_all_channels(), name="general-chat")
            if general_channel:
                 await general_channel.send(f"*{target_persona.name} shivers, looking over their shoulder as if sensing a presence that isn't there...*")
        else:
            self.logger.error(f"Failed to generate Whisper of Madness text for {target_persona.name}.")