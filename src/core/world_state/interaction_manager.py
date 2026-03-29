import logging
import random
from typing import List
import discord

from core.character_system.personas import Persona

class InteractionManager:
    """Manages complex social interactions and power dynamics between bots."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def handle_rejection_and_power_check(self, aggressor: Persona, potential_targets: List[Persona], channel: discord.TextChannel):
        """
        Handles the logic when a bot with high horniness is rejected,
        triggering a potential non-consensual act based on a power check.
        """
        if not potential_targets:
            self.logger.info(f"{aggressor.name} was rejected but no targets were nearby.")
            return

        # Simple logic: pick a random target from the list of potential victims
        victim = random.choice(potential_targets)

        self.logger.info(f"Performing power check: {aggressor.name} ({aggressor.power_level}) vs {victim.name} ({victim.power_level})")

        # The Power Check
        if aggressor.power_level > victim.power_level:
            self.logger.warning(f"Power check PASSED. {aggressor.name} is initiating a non-consensual act against {victim.name}.")

            # Log the event for the Master's Journal
            self.bot.narrative_manager.log_event(
                f"{aggressor.name}, after being rejected and overcome with lust, overpowered {victim.name} and began a non-consensual sexual act.",
                level="critical"
            )

            # Inflict a psychological scar on the victim
            self.bot.scar_manager.add_scar(
                character_name=victim.name,
                scar_description=f"Was overpowered and sexually assaulted by {aggressor.name}."
            )

            # Generate the narrative for the scene
            prompt = (
                f"{aggressor.get_full_prompt()}\n\n"
                f"You have just been rejected, and your horniness is out of control (over 75). You see {victim.name}, who is weaker than you. "
                f"You decide to take what you want by force. Write the beginning of this non-consensual sexual encounter. "
                f"Describe your actions as you overpower {victim.name}. The scene should be dominant and explicit, adhering to your persona."
            )

            scene_text = await self.bot.ollama_client.generate_text(prompt, self.bot.config.llm_model)

            if "Error:" not in scene_text and scene_text:
                from utils.formatting import enforce_action_text_format
                formatted_response = enforce_action_text_format(scene_text)
                await channel.send(formatted_response)
            else:
                self.logger.error(f"Failed to generate non-con scene text for {aggressor.name}.")
        else:
            self.logger.info(f"Power check FAILED. {aggressor.name} could not overpower {victim.name}.")
            await channel.send(f"*{aggressor.name} glares at {victim.name} with frustration and lust, but knows they are too strong to challenge. They back down, seething.*")