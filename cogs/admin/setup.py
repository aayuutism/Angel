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

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You do not have permission to use admin commands.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="setup", description="Admin: Automatically create profile and matches channels.")
    @app_commands.default_permissions(administrator=True)
    async def setup_channels(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        category = await guild.create_category("💕 MATCHMAKING")
        male_channel = await guild.create_text_channel("male-profiles", category=category)
        female_channel = await guild.create_text_channel("female-profiles", category=category)
        matches_channel = await guild.create_text_channel("matches", category=category)

        config = load_config()
        guild_id_str = str(guild.id)
        if guild_id_str not in config:
            config[guild_id_str] = {}

        config[guild_id_str]["male"] = male_channel.id
        config[guild_id_str]["female"] = female_channel.id
        config[guild_id_str]["matches"] = matches_channel.id
        save_config(config)

        await interaction.followup.send(
            f"✅ **Matchmaking system successfully set up!**\n"
            f"• Male Profiles: {male_channel.mention}\n"
            f"• Female Profiles: {female_channel.mention}\n"
            f"• Matches Channel: {matches_channel.mention}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
