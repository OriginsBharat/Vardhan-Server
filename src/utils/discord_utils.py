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
    # Discord channel names are lowercase and use hyphens instead of spaces.
    normalized_channel_name = channel_name.lower().replace(' ', '-')

    for channel in category.text_channels:
        if channel.name == normalized_channel_name:
            logger.info(f"Found existing channel: #{channel.name} in {category.name}")
            return channel

    logger.info(f"Creating new channel: #{normalized_channel_name} in {category.name}")
    return await guild.create_text_channel(normalized_channel_name, category=category, nsfw=nsfw)