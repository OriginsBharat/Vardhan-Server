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
        print(f"Created category: {name}")
    return category

async def get_or_create_channel(guild, name, category=None, nsfw=False, is_private=False, target=None, type=discord.ChannelType.text):
    """Gets a channel by name, or creates it if it doesn't exist."""
    # Check for existing channel within the category
    if category:
        channel = discord.utils.get(category.channels, name=name.lower().replace(" ", "-"))
    else:
        channel = discord.utils.get(guild.channels, name=name.lower().replace(" ", "-"))

    if not channel:
        overwrites = {}
        if is_private and target:
            overwrites[guild.default_role] = discord.PermissionOverwrite(read_messages=False)
            overwrites[target] = discord.PermissionOverwrite(read_messages=True)
            overwrites[guild.me] = discord.PermissionOverwrite(read_messages=True)

        channel_name = name.lower().replace(" ", "-")
        if type == discord.ChannelType.text:
            channel = await guild.create_text_channel(channel_name, category=category, nsfw=nsfw, overwrites=overwrites)
        elif type == discord.ChannelType.voice:
            channel = await guild.create_voice_channel(channel_name, category=category, overwrites=overwrites)
        print(f"Created channel: #{channel.name} in category '{category.name}'")

    return channel

async def get_or_create_role(guild, name, color=discord.Color.default()):
    """Gets a role by name, or creates it if it doesn't exist."""
    role = discord.utils.get(guild.roles, name=name)
    if not role:
        role = await guild.create_role(name=name, color=color)
        print(f"Created role: {name}")
    return role