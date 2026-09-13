import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageOps, ImageDraw
import io
import aiohttp

class AdminMatchmakingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="match", description="Official match two users and generate a banner.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user1="First user", user2="Second user")
    async def match_users(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        await interaction.response.defer()

        # Generate banner helper function
        async def make_banner(u1: discord.Member, u2: discord.Member) -> discord.File:
            async with aiohttp.ClientSession() as session:
                async with session.get(u1.display_avatar.url) as resp1:
                    avatar1_bytes = await resp1.read()
                async with session.get(u2.display_avatar.url) as resp2:
                    avatar2_bytes = await resp2.read()

            bg_color = (60, 30, 45) # Matchmaking dark pink/maroon theme
            banner = Image.new("RGBA", (800, 400), bg_color)
            
            # Process Avatars into circular icons
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

            # Paste Avatars onto the banner background
            banner.paste(av1, (120, 80), av1)
            banner.paste(av2, (480, 80), av2)

            # Draw 'X' between avatars and names
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
