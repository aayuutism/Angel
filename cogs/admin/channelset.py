import discord
from discord.ext import commands
from discord import app_commands
import json
import os

CONFIG_FILE = "channel_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

CHANNEL_CONFIG = load_config()

class ChannelConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Restrict the entire cog or specific commands to Administrators
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You do not have permission to use admin commands.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="channelset", description="Admin: Set the destination channel for male or female profiles.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(gender=[
        app_commands.Choice(name="Male", value="male"),
        app_commands.Choice(name="Female", value="female")
    ])
    @app_commands.describe(gender="Choose profile category", channel="Target text channel")
    async def channel_set(self, interaction: discord.Interaction, gender: str, channel: discord.TextChannel):
        guild_id_str = str(interaction.guild.id)
        if guild_id_str not in CHANNEL_CONFIG:
            CHANNEL_CONFIG[guild_id_str] = {}
        
        CHANNEL_CONFIG[guild_id_str][gender] = channel.id
        save_config(CHANNEL_CONFIG)

        await interaction.response.send_message(f"✅ Successfully set the **{gender}** profile channel to {channel.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChannelConfigCog(bot))
