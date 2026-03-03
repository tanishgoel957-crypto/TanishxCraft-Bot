import discord
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Global sync (works in all servers)
        await self.tree.sync()
        print("Global slash commands synced.")

bot = MyBot()

# =========================
# Ticket Create Button View
# =========================

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket 🎟", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )

        await channel.send(
            f"{user.mention} 🎫 Your ticket has been created!",
            view=CloseView()
        )

        await interaction.response.send_message(
            "✅ Ticket created!",
            ephemeral=True
        )

# =========================
# Close Ticket Button
# =========================

class CloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🔒", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.channel.delete()

# =========================
# Slash Command: /panel
# =========================

@bot.tree.command(name="panel", description="Create the support ticket panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟 Support Tickets",
        description="Click the button below to create a support ticket.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed,
        view=TicketView()
    )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("TOKEN"))
