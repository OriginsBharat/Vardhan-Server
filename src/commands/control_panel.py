import discord

class ControlPanel:
    """Handles the Master's control panel commands in the private channel."""
    def __init__(self, bot):
        self.bot = bot

    async def handle_command(self, message):
        """Parses and executes control panel commands."""
        parts = message.content.lower().split()
        command = parts[0]

        # This function will act as a router for all commands.
        if command == "!adjust" and len(parts) == 4:
            await self.adjust_emotion(message, parts[1], parts[2], parts[3])
        elif command == "!possess" and len(parts) == 2:
            await self.possess_character(message, parts[1])
        elif command == "!release" and len(parts) == 1:
            await self.release_character(message)
        # Add other command handlers here as they are built.
        else:
            # Simple fallback for unrecognized commands
            await message.channel.send(f"Unknown command: `{message.content}`")

    async def adjust_emotion(self, message, character_name, emotion, value_str):
        """Adjusts a specific emotion for a character."""
        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            await message.channel.send(f"Error: Character '{character_name}' not found.")
            return

        if emotion not in persona.emotions:
            await message.channel.send(f"Error: Invalid emotion '{emotion}'. Valid emotions are: {', '.join(persona.emotions.keys())}")
            return

        try:
            value = int(value_str)
            if not 0 <= value <= 100:
                raise ValueError

            # Directly set the value, not adjust by it
            persona.emotions[emotion] = value
            await message.channel.send(f"✅ Successfully set **{persona.name}'s** `{emotion}` to **{value}**.")

            # Check for scene trigger
            if emotion == 'lust' and value > 90:
                 await message.channel.send(f"🔥 **Scene Trigger:** {persona.name}'s lust is critical! They will act on it now.")
                 # This is where you would call a function to make the bot act
                 # e.g., await self.bot.trigger_action(persona, 'high_lust')

        except ValueError:
            await message.channel.send("Error: Value must be an integer between 0 and 100.")

    async def possess_character(self, message, character_name):
        """Allows the Master to take control of a character's bot account."""
        # This is a simplified placeholder. A real multi-bot implementation is complex.
        # We'll simulate it by having the MasterBot speak on behalf of the character.
        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            await message.channel.send(f"Error: Character '{character_name}' not found.")
            return

        self.bot.possessed_character_name = persona.name
        self.bot.master_possessing = True
        await message.channel.send(f"🎭 You are now possessing **{persona.name}**. Any message you send in any channel will be spoken by them. Use `!release` to stop.")

        # Apply sanity penalty for the trauma of being possessed
        persona.adjust_emotion('sanity', -25)


    async def release_character(self, message):
        """Releases control of a possessed character."""
        if not self.bot.master_possessing:
            await message.channel.send("You are not possessing any character.")
            return

        possessed_name = self.bot.possessed_character_name
        self.bot.possessed_character_name = None
        self.bot.master_possessing = False
        await message.channel.send(f"🎭 You have released control of **{possessed_name}**.")