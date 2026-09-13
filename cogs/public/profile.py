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

CHANNEL_CONFIG = load_config()
PROFILES = {}

class ProfileModal(discord.ui.Modal, title="Hoshi — Profile"):
    name = discord.ui.TextInput(
        label="What name should we display?",
        placeholder="Your display name...",
        max_length=50
    )
    age = discord.ui.TextInput(
        label="Your age",
        placeholder="Must be a number...",
        max_length=3
    )
    hobbies = discord.ui.TextInput(
        label="Your hobbies / interests",
        style=discord.TextStyle.paragraph,
        placeholder="Tell us about your hobbies...",
        max_length=300
    )
    looking_for = discord.ui.TextInput(
        label="What are you looking for in a partner?",
        style=discord.TextStyle.paragraph,
        placeholder="What kind of partner are you looking for?",
        max_length=300
    )

    def __init__(self, gender: str):
        super().__init__()
        self.gender = gender

    async def on_submit(self, interaction: discord.Interaction):
        try:
            age_int = int(self.age.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Age must be a valid number.", ephemeral=True)
            return

        guild_id_str = str(interaction.guild.id)
        guild_channels = CHANNEL_CONFIG.get(guild_id_str, {})
        target_channel_id = guild_channels.get(self.gender)

        if not target_channel_id:
            await interaction.response.send_message(f"❌ The **{self.gender}** profile channel hasn't been set by an admin yet using `/channelset`.", ephemeral=True)
            return

        channel = interaction.client.get_channel(target_channel_id)
        if not channel:
            await interaction.response.send_message("❌ Configured channel could not be found. Please ask an admin to reconfigure it.", ephemeral=True)
            return

        PROFILES[interaction.user.id] = {
            "name": self.name.value,
            "age": age_int,
            "gender": self.gender,
            "hobbies": self.hobbies.value,
            "looking_for": self.looking_for.value,
            "likes": [],
            "wants_match": []
        }

        embed = discord.Embed(
            title="A NEW PROFILE HAS BLOOMED",
            description="--------------------------------------------------",
            color=0xffc0cb
        )
        embed.set_author(name=self.name.value, icon_url=interaction.user.display_avatar.url)
        
        embed.add_field(name="NAME", value=self.name.value, inline=False)
        embed.add_field(name="AGE", value=str(age_int), inline=False)
        embed.add_field(name="GENDER", value=self.gender, inline=False)
        embed.add_field(name="HOBBIES", value=self.hobbies.value, inline=False)
        embed.add_field(name="LOOKING FOR", value=self.looking_for.value, inline=False)
        embed.add_field(name="--------------------------------------------------", value=f"liked by\n*No likes yet*\n\nwants to be matched with them\n*None*\n\nmember id: {interaction.user.id}", inline=False)

        msg = await channel.send(embed=embed, view=MatchProfileView(profile_owner_id=interaction.user.id))
        PROFILES[interaction.user.id]["message_id"] = msg.id

        await interaction.response.send_message("✅ Your profile has been successfully created and posted to the designated channel!", ephemeral=True)


class MatchProfileView(discord.ui.View):
    def __init__(self, profile_owner_id: int):
        super().__init__(timeout=None)
        self.profile_owner_id = profile_owner_id

    @discord.ui.button(label="Like Profile", style=discord.ButtonStyle.secondary, custom_id="like_profile_btn")
    async def like_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        profile = PROFILES.get(self.profile_owner_id)
        if not profile:
            await interaction.response.send_message("❌ Profile not found.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        if user_id in profile["likes"]:
            profile["likes"].remove(user_id)
            await interaction.response.send_message("💔 You unliked this profile.", ephemeral=True)
        else:
            profile["likes"].append(user_id)
            await interaction.response.send_message("💖 You liked this profile!", ephemeral=True)
        
        await self.update_message(interaction)

    @discord.ui.button(label="Get Matched", style=discord.ButtonStyle.primary, custom_id="get_matched_btn")
    async def get_matched(self, interaction: discord.Interaction, button: discord.ui.Button):
        profile = PROFILES.get(self.profile_owner_id)
        if not profile:
            await interaction.response.send_message("❌ Profile not found.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        if user_id in profile["wants_match"]:
            profile["wants_match"].remove(user_id)
            await interaction.response.send_message("❌ Removed your match signal.", ephemeral=True)
        else:
            profile["wants_match"].append(user_id)
            await interaction.response.send_message("✨ Signal sent to admins that you want to be matched with this profile!", ephemeral=True)

        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        profile = PROFILES.get(self.profile_owner_id)
        if not profile:
            return

        liked_str = ", ".join([f"<@{uid}>" for uid in profile["likes"]]) if profile["likes"] else "*No likes yet*"
        wants_str = ", ".join([f"<@{uid}>" for uid in profile["wants_match"]]) if profile["wants_match"] else "*None*"

        embed = interaction.message.embeds[0]
        embed.set_field_at(
            len(embed.fields) - 1,
            name="--------------------------------------------------",
            value=f"liked by\n{liked_str}\n\nwants to be matched with them\n{wants_str}\n\nmember id: {self.profile_owner_id}",
            inline=False
        )
        await interaction.message.edit(embed=embed, view=self)


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createprofile", description="Privately create your matchmaking profile.")
    @app_commands.choices(gender=[
        app_commands.Choice(name="Male", value="male"),
        app_commands.Choice(name="Female", value="female")
    ])
    @app_commands.describe(gender="Choose whether this is a male or female profile")
    async def createprofile(self, interaction: discord.Interaction, gender: str):
        modal = ProfileModal(gender=gender)
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
