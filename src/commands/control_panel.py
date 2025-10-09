import discord
from discord.ext import commands
import logging

class ControlPanel(commands.Cog):
    """
    Houses all the private commands for the Master to control the world.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.possessed_bot_persona = None
        self.master_user = None
        self.webhooks = {}

    async def cog_check(self, ctx):
        """Checks if the user is the Master."""
        is_master = ctx.author.id == self.bot.config.user_id
        if not is_master:
            await ctx.send("You do not have permission to use this command.", ephemeral=True)
        return is_master

    async def get_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """Gets or creates a webhook for a specific channel."""
        if channel.id in self.webhooks:
            return self.webhooks[channel.id]

        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user == self.bot.user:
                self.webhooks[channel.id] = webhook
                self.logger.info(f"Found existing webhook for channel #{channel.name}")
                return webhook

        self.logger.info(f"Creating new webhook for channel #{channel.name}")
        new_webhook = await channel.create_webhook(name=f"{self.bot.user.name} Relay")
        self.webhooks[channel.id] = new_webhook
        return new_webhook

    @commands.group(name="master", invoke_without_command=True)
    async def master(self, ctx):
        """Base command for Master controls."""
        await ctx.send("Welcome, Master. Use `!master adjust`, `!master create_emotion`, `!master possess`, etc. to command your world.", ephemeral=True)

    @master.command(name="adjust")
    async def adjust(self, ctx, character_name: str, emotion: str, value: int):
        """Adjusts an emotional slider for a character."""
        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            return await ctx.send(f"Error: Persona '{character_name}' not found.", ephemeral=True)

        emotion = emotion.lower()
        if emotion not in persona.emotions:
            return await ctx.send(f"Error: Emotion '{emotion}' not found for {character_name}. Use `!master create_emotion` to add it.", ephemeral=True)

        persona.emotions[emotion] = value
        self.logger.info(f"Master adjusted {character_name}'s {emotion} to {value}.")
        await ctx.send(f"✅ Adjusted **{character_name}**'s `{emotion}` to `{value}`.", ephemeral=True)

    @master.command(name="create_emotion")
    async def create_emotion(self, ctx, character_name: str, emotion: str, default_value: int = 50):
        """Creates a new emotional slider for a character."""
        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            return await ctx.send(f"Error: Persona '{character_name}' not found.", ephemeral=True)

        emotion = emotion.lower()
        if emotion in persona.emotions:
            return await ctx.send(f"Error: Emotion '{emotion}' already exists for {character_name}.", ephemeral=True)

        persona.emotions[emotion] = default_value
        self.logger.info(f"Master created new emotion '{emotion}' for {character_name} with value {default_value}.")
        await ctx.send(f"✅ Created new emotion `{emotion}` for **{character_name}** with a default value of `{default_value}`.", ephemeral=True)

    @master.command(name="possess")
    async def possess(self, ctx, character_name: str):
        """Possesses a bot, making them speak your words."""
        if self.possessed_bot_persona:
            return await ctx.send(f"Error: You are already possessing {self.possessed_bot_persona.name}. Use `!master release` first.", ephemeral=True)

        persona = self.bot.persona_manager.get_persona(character_name)
        if not persona:
            return await ctx.send(f"Error: Persona '{character_name}' not found.", ephemeral=True)

        self.possessed_bot_persona = persona
        self.master_user = ctx.author
        await ctx.send(f"🎭 You are now possessing **{character_name}**. Any message you send will be spoken by them. Use `!master release` to stop.", ephemeral=True)
        self.logger.info(f"Master is now possessing {character_name}.")

    @master.command(name="release")
    async def release(self, ctx):
        """Releases a possessed bot."""
        if not self.possessed_bot_persona:
            return await ctx.send("Error: You are not possessing any bot.", ephemeral=True)

        released_name = self.possessed_bot_persona.name
        self.possessed_bot_persona = None
        self.master_user = None
        await ctx.send(f"✅ You have released **{released_name}**.", ephemeral=True)
        self.logger.info(f"Master released {released_name}.")

    @master.command(name="help")
    async def help(self, ctx):
        """Posts a list of all available commands to the bot-commands-list channel."""
        embed = discord.Embed(
            title="📜 Master Command List",
            description="A comprehensive list of commands to control the world.",
            color=discord.Color.gold()
        )

        for command in self.master.commands:
            if command.name != 'help':
                signature = f"!master {command.name} {command.signature}"
                embed.add_field(name=f"`{signature}`", value=command.help or "No description provided.", inline=False)

        commands_list_channel = discord.utils.get(ctx.guild.channels, name="bot-commands-list")
        if commands_list_channel:
            try:
                await commands_list_channel.send(embed=embed)
                await ctx.send("✅ A list of all available commands has been posted in #bot-commands-list.", ephemeral=True)
            except discord.Forbidden:
                await ctx.send("Error: I lack permission to send messages in #bot-commands-list.", ephemeral=True)
        else:
            await ctx.send("Warning: #bot-commands-list channel not found. Sending commands here instead.", embed=embed, ephemeral=True)

    async def handle_possession(self, message: discord.Message):
        """
        This method is called by the bot's on_message event when possession is active.
        """
        if message.content.lower().strip() == "!master release":
            await self.bot.process_commands(message)
            return

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        try:
            webhook = await self.get_webhook(message.channel)
            avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else None
            await webhook.send(
                content=message.content,
                username=self.possessed_bot_persona.name,
                avatar_url=avatar_url
            )
        except Exception as e:
            self.logger.error(f"Failed to send possessed message via webhook: {e}")
            try:
                await message.author.send(f"**Possession Error:** Could not send message as {self.possessed_bot_persona.name} in #{message.channel.name}.")
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(ControlPanel(bot))