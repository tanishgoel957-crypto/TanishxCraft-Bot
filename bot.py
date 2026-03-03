import discord
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1439766744758489111  # your server ID

intents = discord.Intents.default()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print("Slash commands synced.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ping", description="Test if the bot is working")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot is working.")

bot.run(TOKEN)
