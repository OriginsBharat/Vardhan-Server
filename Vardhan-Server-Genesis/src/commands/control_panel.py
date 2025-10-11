import discord
from discord.ext import commands
import logging

class ControlPanelCog(commands.Cog, name="Master Controls"):
    """
    A cog for the core Master control panel commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.group(name="master", invoke_without_command=True)
    @commands.is_owner()
    async def master(self, ctx):
        """Base command for the Master Control Panel. Shows help."""
        help_text = (
            "**Crucible Core Control**\n\n"
            "`!master view <BotName>` - View a bot's current emotions.\n"
            "`!master adjust <BotName> <Emotion> <Value>` - Set a bot's emotion (0.0-1.0).\n"
            "`!master create_emotion <BotName> <EmotionName>` - Create a new emotional slider for a bot."
        )
        await ctx.send(embed=discord.Embed(title="Master Commands", description=help_text, color=0xFFD700))

    @master.command(name="view")
    @commands.is_owner()
    async def view_emotions(self, ctx, character_name: str = None):
        """Views the emotional state of a character."""
        if not character_name:
            await ctx.send("Usage: `!master view <BotName>`")
            return

        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            await ctx.send(f"Error: Bot '{character_name}' not found.")
            return

        emotions = persona.emotions
        emo_text = "\n".join([f"**{k.capitalize()}:** {v:.2f}" for k, v in emotions.items()])
        embed = discord.Embed(title=f"Emotional State: {persona.name}", description=emo_text, color=persona.aura_color)
        await ctx.send(embed=embed)

    @master.command(name="adjust")
    @commands.is_owner()
    async def adjust_emotion(self, ctx, character_name: str = None, emotion: str = None, value_str: str = None):
        """Adjusts an emotion for a character."""
        if not all([character_name, emotion, value_str]):
            await ctx.send("Usage: `!master adjust <BotName> <Emotion> <Value>`")
            return

        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            await ctx.send(f"Error: Bot '{character_name}' not found.")
            return

        if emotion.lower() not in persona.emotions:
            await ctx.send(f"Error: Emotion '{emotion}' not found for {character_name}. Use `!master create_emotion` first.")
            return

        try:
            value = float(value_str)
            if not 0.0 <= value <= 1.0:
                raise ValueError()
            persona.emotions[emotion.lower()] = value
            await ctx.send(f"✅ Set **{character_name}'s** `{emotion.lower()}` to **{value:.2f}**.")
        except (ValueError, TypeError):
            await ctx.send("Error: Value must be a number between 0.0 and 1.0.")

    @master.command(name="create_emotion")
    @commands.is_owner()
    async def create_emotion(self, ctx, character_name: str = None, emotion: str = None):
        """Creates a new emotional slider for a character."""
        if not all([character_name, emotion]):
            await ctx.send("Usage: `!master create_emotion <BotName> <EmotionName>`")
            return

        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            await ctx.send(f"Error: Bot '{character_name}' not found.")
            return

        emotion = emotion.lower()
        if emotion in persona.emotions:
            await ctx.send(f"Error: Emotion '{emotion}' already exists for {character_name}.")
            return

        persona.emotions[emotion] = 0.5 # Default to a neutral value
        await ctx.send(f"✅ Created new emotion `{emotion}` for **{character_name}** with a default value of 0.5.")

async def setup(bot):
    """The setup function for the cog."""
    await bot.add_cog(ControlPanelCog(bot))
    logging.getLogger(__name__).info("ControlPanelCog loaded.")