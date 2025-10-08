import discord
import logging

logger = logging.getLogger(__name__)

async def get_or_create_category(guild: discord.Guild, category_name: str, overwrites=None) -> discord.CategoryChannel:
    """
    Finds a category by name or creates it if it doesn't exist.

    Args:
        guild: The discord.Guild to search in.
        category_name: The name of the category to find or create.
        overwrites: The permission overwrites for the category.

    Returns:
        The discord.CategoryChannel object.
    """
    for category in guild.categories:
        if category.name.lower() == category_name.lower():
            logger.info(f"Found existing category: {category_name}")
            return category

    logger.info(f"Creating new category: {category_name}")
    return await guild.create_category(category_name, overwrites=overwrites)

async def get_or_create_channel(guild: discord.Guild, channel_name: str, category: discord.CategoryChannel, nsfw=False) -> discord.TextChannel:
    """
    Finds a text channel by name within a category or creates it if it doesn't exist.

    Args:
        guild: The discord.Guild to search in.
        channel_name: The name of the channel to find or create.
        category: The discord.CategoryChannel to place the channel in.
        nsfw: Whether the channel should be marked as NSFW.

    Returns:
        The discord.TextChannel object.
    """
    for channel in category.text_channels:
        if channel.name.lower() == channel_name.lower():
            logger.info(f"Found existing channel: {channel_name} in {category.name}")
            return channel

    logger.info(f"Creating new channel: #{channel_name} in {category.name}")
    return await guild.create_text_channel(channel_name, category=category, nsfw=nsfw)