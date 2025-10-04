# src/commands/control_panel.py
# Contains the logic for the private control panel commands.

import discord
import logging
from typing import List

from src.core.character_system.personas import Character
from src.utils.discord_utils import create_embed

class ControlPanelCommand:
    """
    Handles the logic for the control panel commands, which allow the Master
    to view and adjust the emotional state of the bots.
    """
    def __init__(self, characters: List[Character]):
        self.characters = characters
        # Define the emotional "sliders" that can be adjusted.
        self.valid_emotions = ["mood", "love", "lust", "dominance"]
        logging.info("ControlPanelCommand initialized.")

    async def execute(self, message: discord.Message):
        """Executes the control panel command based on the message content."""
        args = message.content.lower().split()

        # Command: !status
        if args[0] == "!status":
            await self.show_panel(message.channel)
            return

        # Command: !set <Character> <Emotion> <Value>
        if args[0] == "!set" and len(args) == 4:
            character_name = args[1].title()
            emotion = args[2]
            try:
                value = int(args[3])
                await self.set_emotion(message, character_name, emotion, value)
            except ValueError:
                await message.channel.send("Invalid value. Emotion value must be a number (e.g., 0-100).")
            return

        await message.channel.send("Invalid command. Use `!status` or `!set <Name> <Emotion> <Value>`.")

    async def show_panel(self, channel: discord.TextChannel):
        """Displays the current emotional state of all bots."""
        description = "Current state of all characters:\n\n"
        for char in self.characters:
            # This can be expanded to show more emotional variables later
            description += f"**{char.name}**\n"
            description += f"- **Status:** {char.status}\n"
            description += f"- **Mood:** {char.mood}\n\n"

        embed = create_embed(
            title="Master Control Panel",
            description=description,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Use '!set <Name> <Emotion> <Value>' to make changes.")
        await channel.send(embed=embed)

    async def set_emotion(self, message: discord.Message, character_name: str, emotion: str, value: int):
        """Sets an emotional value for a specific character."""
        if emotion not in self.valid_emotions:
            await message.channel.send(f"Invalid emotion '{emotion}'. Valid emotions are: {', '.join(self.valid_emotions)}")
            return

        character = next((c for c in self.characters if c.name == character_name), None)
        if not character:
            await message.channel.send(f"Character '{character_name}' not found.")
            return

        # Use setattr to dynamically change the character's attribute.
        # This is a placeholder for a more robust emotional system.
        # For now, we'll just focus on mood.
        if emotion == "mood":
            # For mood, we'd map the value to a state, but for now, we'll just note it.
            # This part needs a more complex implementation to be a true "slider".
            # For now, we'll just acknowledge the command.
            character.mood = f"Set to '{emotion}' with value {value}" # Placeholder update
            await message.channel.send(f"**{character.name}'s** '{emotion}' has been adjusted to **{value}**.")
        else:
            await message.channel.send(f"Adjusting '{emotion}' is not fully implemented yet, but the command is recognized.")