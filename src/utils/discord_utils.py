import discord

async def get_or_create_category(guild, name, is_private=False, target=None):
    """Gets a category by name, or creates it if it doesn't exist."""
    category = discord.utils.get(guild.categories, name=name)
    if not category:
        overwrites = {}
        if is_private and target:
            # Private to the target user (Master) and the bot
            overwrites[guild.default_role] = discord.PermissionOverwrite(read_messages=False)
            overwrites[target] = discord.PermissionOverwrite(read_messages=True)
            overwrites[guild.me] = discord.PermissionOverwrite(read_messages=True)
        category = await guild.create_category(name, overwrites=overwrites)
    return category

async def get_or_create_channel(guild, name, category=None, nsfw=False, is_private=False, target=None, type=discord.ChannelType.text):
    """Gets a channel by name, or creates it if it doesn't exist."""
    channel = discord.utils.get(guild.channels, name=name, category=category)
    if not channel:
        overwrites = {}
        if is_private and target:
            overwrites[guild.default_role] = discord.PermissionOverwrite(read_messages=False)
            overwrites[target] = discord.PermissionOverwrite(read_messages=True)
            overwrites[guild.me] = discord.PermissionOverwrite(read_messages=True)

        if type == discord.ChannelType.text:
            channel = await guild.create_text_channel(name, category=category, nsfw=nsfw, overwrites=overwrites)
        elif type == discord.ChannelType.voice:
            channel = await guild.create_voice_channel(name, category=category, overwrites=overwrites)

    return channel

async def get_or_create_role(guild, name, color=discord.Color.default()):
    """Gets a role by name, or creates it if it doesn't exist."""
    role = discord.utils.get(guild.roles, name=name)
    if not role:
        role = await guild.create_role(name=name, color=color)
    return role