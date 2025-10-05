# src/utils/discord_utils.py
# Helper functions for common Discord interactions.

import discord
import logging

def create_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """
    Creates a standardized Discord embed.

    Args:
        title: The title of the embed.
        description: The main text content of the embed.
        color: The color of the embed's side strip.

    Returns:
        A discord.Embed object ready to be sent.
    """
    return discord.Embed(
        title=title,
        description=description,
        color=color
    )

async def send_dm(user: discord.User, message: str):
    """
    Sends a direct message to a user.

    Args:
        user: The discord.User object to send the DM to.
        message: The content of the message.
    """
    try:
        await user.send(message)
    except discord.Forbidden:
        logging.error(f"Could not send DM to {user.name}. They may have DMs disabled.")
    except Exception as e:
        logging.error(f"An error occurred while sending a DM to {user.name}: {e}")