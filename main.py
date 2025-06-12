import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True

# Bot setup
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# Constants
WELCOME_CHANNEL_NAME = "welcome-home"
AUTO_ROLE_NAME = "🌼 Resident"
REACTION_ROLE_CHANNEL = "constellations"
MODERATOR_ROLE_ID = 1378302078258122913
LOG_CHANNEL_NAME = "celestial-overseer"

# Emoji-role mapping
emoji_to_role = {
    "🕊️": "🕊️ Peacekeeper",
    "🌿": "🌿 Calm Presence",
    "🫧": "🫧 Bubble of Joy",
    "🍵": "🍵 Tea Drinker",
    "🧷": "🧷 Soft Anchor",
    "🕯️": "🕯️ Quiet Flame",
    "🌧️": "🌧️ Rainy Day Dreamer",
    "🧵": "🧵 Threadweaver",
    "🪞": "🪞 Gentle Mirror",
    "🌙": "🌙 Lunar Listener",
    "🛡️": "🛡️ Guardian",
    "🫖": "🫖 Quiet Companion",
    "🌅": "🌅 Dawnbringer",
    "🌞": "🌞 Daydreamer",
    "🪄": "🪄 Stargazer",
    "🦉": "🦉 Night Owl",
    "🐦": "🐦 Early Bird",
    "🧘": "🧘 Inner Mystic",
    "🪶": "🪶 Soft Thinker",
    "🌠": "🌠 Wishing Star",
    "📖": "📖 Storyteller"
}

# Permissions
def is_keyholder(interaction: discord.Interaction) -> bool:
    return any(role.id == MODERATOR_ROLE_ID for role in interaction.user.roles)

async def log_action(guild: discord.Guild, content: str):
    log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(f"📜 {content}")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} is ready and commands are synced.")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        await member.add_roles(role)
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"🌸 Welcome home, {member.mention} 🌸")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member is None or payload.member.bot:
        return
    guild = bot.get_guild(payload.guild_id)
    emoji = str(payload.emoji)
    role_name = emoji_to_role.get(emoji)
    if not role_name:
        return
    role = discord.utils.get(guild.roles, name=role_name)
    member = guild.get_member(payload.user_id)
    if role and member:
        await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        return
    emoji = str(payload.emoji)
    role_name = emoji_to_role.get(emoji)
    if not role_name:
        return
    role = discord.utils.get(guild.roles, name=role_name)
    if role and role in member.roles:
        await member.remove_roles(role)

# Slash Commands

@tree.command(name="resetroles", description="Remove all your reaction roles.")
async def resetroles_command(interaction: discord.Interaction):
    member = interaction.user
    removed = []
    for emoji, role_name in emoji_to_role.items():
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role and role in member.roles:
            await member.remove_roles(role)
            removed.append(role.name)
    if removed:
        await interaction.response.send_message(
            f"Removed roles: {', '.join(removed)}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "You don't have any of the reaction roles.", ephemeral=True
        )

@tree.command(name="kick", description="Kick a member (Keyholders only)")
async def kick_command(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member} was kicked. Reason: {reason}")
    await log_action(interaction.guild, f"🦶 {interaction.user.mention} kicked {member.mention} — Reason: {reason}")

@tree.command(name="ban", description="Ban a member (Keyholders only)")
async def ban_command(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member} was banned. Reason: {reason}")
    await log_action(interaction.guild, f"🔨 {interaction.user.mention} banned {member.mention} — Reason: {reason}")

@tree.command(name="timeout", description="Timeout a member temporarily (Keyholders only)")
async def timeout_command(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until=duration, reason=reason)
    await interaction.response.send_message(f"{member} has been timed out for {minutes} minute(s).")
    await log_action(interaction.guild, f"⏳ {interaction.user.mention} timed out {member.mention} for {minutes} min — Reason: {reason}")

@tree.command(name="untimeout", description="Remove timeout from a member (Keyholders only)")
async def untimeout_command(interaction: discord.Interaction, member: discord.Member):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    await member.timeout(until=None)
    await interaction.response.send_message(f"{member}'s timeout has been lifted.")
    await log_action(interaction.guild, f"✅ {interaction.user.mention} removed timeout from {member.mention}")

@tree.command(name="purge", description="Delete messages from a specific user (Keyholders only)")
@app_commands.describe(user="The user whose messages to delete", limit="Max number of messages to search (default 100)")
async def purge_command(interaction: discord.Interaction, user: discord.User, limit: int = 100):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
        await interaction.response.send_message("I need 'Manage Messages' permission in this channel.", ephemeral=True)
        return
    deleted = []
    async for message in interaction.channel.history(limit=limit):
        if message.author.id == user.id:
            deleted.append(message)
    if not deleted:
        await interaction.response.send_message(f"No messages from {user.mention} found in the last {limit}.", ephemeral=True)
        return
    await interaction.channel.delete_messages(deleted)
    await interaction.response.send_message(f"Deleted {len(deleted)} message(s) from {user.mention}.", ephemeral=True)
    await log_action(interaction.guild, f"🧹 {interaction.user.mention} purged {len(deleted)} messages from {user.mention} in {interaction.channel.mention}")

@tree.command(name="resetreactionroles", description="Reset the reaction role embeds (Keyholders only)")
async def resetreactionroles_command(interaction: discord.Interaction):
    if not is_keyholder(interaction):
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)  # Prevent timeout

    channel = discord.utils.get(interaction.guild.text_channels, name=REACTION_ROLE_CHANNEL)
    if not channel:
        await interaction.followup.send("Reaction role channel not found.", ephemeral=True)
        return

    async for msg in channel.history(limit=100):
        if msg.author == bot.user:
            await msg.delete()
@bot.event
async def on_ready():
    print(f"Aya is online as {bot.user}")
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="🌙 Stargazing in the Sanctuary"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    
    embed1 = discord.Embed(
        title="🌿 Choose Your Sanctuary Role",
        description="Select the role that best reflects your grounding energy in the sanctuary. These roles are about your steady presence and inner light.",
        color=0xa3d9a5
    )
    embed1.set_footer(text="🌿 Green = grounding / sanctuary roles")

    embed2 = discord.Embed(
        title="🌌 Choose Your Vibe",
        description="Pick a role that reflects your current mood, vibe, or state of being. These roles are fluid — feel free to change them anytime.",
        color=0xb3cde0
    )
    embed2.set_footer(text="🌌 Blue = emotional / mood-based roles")

    sanctuary_roles = ["🕊️", "🌿", "🫧", "🍵", "🧷", "🕯️", "🌧️", "🧵", "🪞", "🌙", "🛡️", "🫖"]
    vibe_roles = ["🌅", "🌞", "🪄", "🦉", "🐦", "🧘", "🪶", "🌠", "📖"]

    embed1_fields = {
        "🕊️ Peacekeeper": "A calming force who eases tension",
        "🌿 Calm Presence": "Gentle and steady, brings peace to others",
        "🫧 Bubble of Joy": "Light-hearted and brings smiles",
        "🍵 Tea Drinker": "Warm and quiet, finds comfort in the simple",
        "🧷 Soft Anchor": "Grounds others with quiet strength",
        "🕯️ Quiet Flame": "Gentle but always present",
        "🌧️ Rainy Day Dreamer": "Softly introspective and soothing",
        "🧵 Threadweaver": "Connects others through thoughtful presence",
        "🪞 Gentle Mirror": "Reflects with empathy and understanding",
        "🌙 Lunar Listener": "Silent support through all phases",
        "🛡️ Guardian": "Protects others with quiet strength",
        "🫖 Quiet Companion": "Present, steady, always here"
    }

    embed2_fields = {
        "🌅 Dawnbringer": "Fresh energy and new beginnings",
        "🌞 Daydreamer": "Cheerful and creative",
        "🪄 Stargazer": "Eyes on the vast unknown",
        "🦉 Night Owl": "Alert and alive when the world sleeps",
        "🐦 Early Bird": "Bright start and focused spirit",
        "🧘 Inner Mystic": "In tune with stillness and insight",
        "🪶 Soft Thinker": "Thoughtful and tender",
        "🌠 Wishing Star": "Hopeful and shining",
        "📖 Storyteller": "Shares warmth through words"
    }

    for name, value in embed1_fields.items():
        embed1.add_field(name=name, value=value, inline=False)
    for name, value in embed2_fields.items():
        embed2.add_field(name=name, value=value, inline=False)

    msg1 = await channel.send(embed=embed1)
    msg2 = await channel.send(embed=embed2)

    for emoji in sanctuary_roles:
        await msg1.add_reaction(emoji)
    for emoji in vibe_roles:
        await msg2.add_reaction(emoji)

    await interaction.followup.send("Reaction role embeds have been reset and reposted.", ephemeral=True)

# Run bot
bot.run(TOKEN)
