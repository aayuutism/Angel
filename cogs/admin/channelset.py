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

class ChannelConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You do not have permission to use admin commands.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="channelset", description="Admin: Manually set a destination channel for profiles or matches.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(category=[
        app_commands.Choice(name="Male Profiles", value="male"),
        app_commands.Choice(name="Female Profiles", value="female"),
        app_commands.Choice(name="Matches Channel", value="matches")
    ])
    @app_commands.describe(category="Choose which category to configure", channel="Target text channel")
    async def channel_set(self, interaction: discord.Interaction, category: str, channel: discord.TextChannel):
        config = load_config()
        guild_id_str = str(interaction.guild.id)
        if guild_id_str not in config:
            config[guild_id_str] = {}
        
        config[guild_id_str][category] = channel.id
        save_config(config)

        await interaction.response.send_message(f"✅ Successfully set the **{category}** channel to {channel.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChannelConfigCog(bot))
