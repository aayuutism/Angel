import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
    # Load cogs
    for folder in os.listdir("./cogs"):
        folder_path = os.path.join("./cogs", folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".py"):
                    cog_name = f"cogs.{folder}.{filename[:-3]}"
                    try:
                        await bot.load_extension(cog_name)
                        print(f"Loaded extension: {cog_name}")
                    except Exception as e:
                        print(f"Failed to load extension {cog_name}: {e}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# bot.run("YOUR_BOT_TOKEN")
