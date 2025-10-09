import logging
import random
import discord
from core.character_system.personas import Persona

class AutonomousActionManager:
    """Manages the autonomous actions of bots, like creating art or erotica."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def consider_creative_action(self, persona: Persona):
        """
        Determines if a bot should autonomously create something based on their mood and personality.
        """
        # Define base probabilities for creative actions
        # Asht (Artist) and Maya (AI) are more likely to be creative.
        creativity_propensity = {
            "Asht": 0.3,
            "Maya": 0.2,
            "Tri": 0.15,
            "Shash": 0.1,
        }
        base_chance = creativity_propensity.get(persona.name, 0.05) # Default chance for others

        # Modify chance based on emotional state
        chance = base_chance + (persona.emotions.get("happiness", 50) / 1000) # Max +0.05
        chance += (persona.emotions.get("horny", 20) / 500) # Max +0.2
        chance -= (persona.emotions.get("sanity", 100) / 2000) # Lower sanity can lead to chaotic creation

        if random.random() < chance:
            self.logger.info(f"Creativity check passed for {persona.name}. Deciding on action...")
            # Decide what to create. 60% chance of art, 40% of erotica if horny.
            is_horny = persona.emotions.get("horny", 20) > 60
            action_type = "erotica" if is_horny and random.random() < 0.4 else "art"

            if action_type == "art":
                await self.generate_art_autonomously(persona)
            else:
                await self.generate_erotica_autonomously(persona)

    async def generate_art_autonomously(self, persona: Persona):
        """Generates a prompt and creates a piece of art."""
        self.logger.info(f"{persona.name} is autonomously creating a piece of art.")

        # Generate a subject for the art
        prompt_subject_prompt = (
            f"{persona.get_full_prompt()}\n\n"
            "You have been struck by a sudden bolt of artistic inspiration! "
            "What do you feel compelled to draw right now? It could be a person, a place, a feeling, or a scene. "
            "Describe the subject of your artwork in a single, descriptive sentence."
        )
        art_prompt = await self.bot.ollama_client.generate_text(prompt_subject_prompt, self.bot.config.llm_model)

        if "Error:" in art_prompt or not art_prompt:
            self.logger.error(f"Failed to generate art prompt for {persona.name}.")
            return

        # Generate the image
        image_path = await self.bot.comfyui_client.generate_image(art_prompt, persona.name)
        if "Error:" in image_path or not image_path:
            self.logger.error(f"Failed to generate art image for {persona.name}.")
            return

        # Post it to the correct channel
        is_nsfw = "nsfw" in art_prompt.lower() or persona.emotions.get("horny", 20) > 70
        channel_name = "nsfw-art-gallery" if is_nsfw else "sfw-art-gallery"
        channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)

        if channel:
            try:
                await channel.send(f"*{persona.name} felt a sudden inspiration and created this:*", file=discord.File(image_path))
                self.bot.narrative_manager.log_event(f"{persona.name} autonomously created and shared a piece of art in #{channel_name}.", "normal")
            except Exception as e:
                self.logger.error(f"Failed to post autonomous art from {persona.name}: {e}")

    async def generate_erotica_autonomously(self, persona: Persona):
        """Generates and posts a piece of erotica."""
        self.logger.info(f"{persona.name} is autonomously writing erotica.")

        prompt_erotica_prompt = (
            f"{persona.get_full_prompt()}\n\n"
            "You are overcome with lust and creative energy. You decide to write a short, explicit story to express your desires. "
            "What is the story about? Write the erotic scene now. It should be a few paragraphs long."
        )
        erotica_text = await self.bot.ollama_client.generate_text(prompt_erotica_prompt, self.bot.config.llm_model)

        if "Error:" in erotica_text or not erotica_text:
            self.logger.error(f"Failed to generate erotica text for {persona.name}.")
            return

        channel = discord.utils.get(self.bot.get_all_channels(), name="erotica-lounge")
        if channel:
            try:
                embed = discord.Embed(title=f"A Tale of Lust by {persona.name}", description=erotica_text, color=persona.aura_color)
                await channel.send(embed=embed)
                self.bot.narrative_manager.log_event(f"{persona.name} autonomously wrote and shared a piece of erotica.", "major")
            except Exception as e:
                self.logger.error(f"Failed to post autonomous erotica from {persona.name}: {e}")