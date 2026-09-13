import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageOps, ImageDraw
import io
import aiohttp

from cogs.public.profile import PROFILES

class AdminMatchmakingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You do not have permission to use admin commands.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="possiblematches", description="Admin: View mutual likes and match signals.")
    @app_commands.default_permissions(administrator=True)
    async def possible_matches(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not PROFILES:
            await interaction.followup.send("❌ No profiles have been created yet.", ephemeral=True)
            return

        embed = discord.Embed(
            title="POSSIBLE MATCHES REPORT",
            description="--------------------------------------------------\nReviewing mutual likes and admin signals...",
            color=0xffc0cb
        )

        found_pairs = 0
        for owner_id, profile in PROFILES.items():
            interested_users = set(profile["likes"] + profile["wants_match"])
            
            for target_id in interested_users:
                target_profile = PROFILES.get(target_id)
                if target_profile:
                    target_interested = set(target_profile["likes"] + target_profile["wants_match"])
                    if owner_id in target_interested:
                        embed.add_field(
                            name=f"Potential Match Found",
                            value=f"<@{owner_id}> 💖 <@{target_id}>",
                            inline=False
                        )
                        found_pairs += 1

        if found_pairs == 0:
            embed.add_field(name="Status", value="No mutual connections or match signals found yet.", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="match", description="Official match two users and generate a banner.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user1="First user", user2="Second user")
    async def match_users(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        await interaction.response.defer()

        async def make_banner(u1: discord.Member, u2: discord.Member) -> discord.File:
            async with aiohttp.ClientSession() as session:
                async with session.get(u1.display_avatar.url) as resp1:
                    avatar1_bytes = await resp1.read()
                async with session.get(u2.display_avatar.url) as resp2:
                    avatar2_bytes = await resp2.read()

            bg_color = (60, 30, 45)
            banner = Image.new("RGBA", (800, 400), bg_color)
            
            def process_avatar(data):
                img = Image.open(io.BytesIO(data)).convert("RGBA").resize((200, 200))
                mask = Image.new("L", (200, 200), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 200, 200), fill=255)
                output = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
                output.paste(img, (0, 0), mask=mask)
                return output

            av1 = process_avatar(avatar1_bytes)
            av2 = process_avatar(avatar2_bytes)

            banner.paste(av1, (120, 80), av1)
            banner.paste(av2, (480, 80), av2)

            draw = ImageDraw.Draw(banner)
            draw.text((385, 160), "×", fill="white")

            draw.text((120, 300), u1.display_name[:15], fill="white")
            draw.text((480, 300), u2.display_name[:15], fill="white")

            buffer = io.BytesIO()
            banner.save(buffer, format="PNG")
            buffer.seek(0)
            return discord.File(buffer, filename="match.png")

        file = await make_banner(user1, user2)
        
        announcement_text = f"{user1.mention} × {user2.mention}\n*may this be the start of something lovely.*"
        
        embed = discord.Embed(title="A MATCH HAS BLOOMED", description="--------------------------------------------------", color=0xffc0cb)
        embed.set_image(url="attachment://match.png")

        await interaction.followup.send(content=announcement_text, embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(AdminMatchmakingCog(bot))
