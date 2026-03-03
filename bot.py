import discord
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True

GUILD_ID = 1439766744758489111  # your server ID here


class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# =========================
# Ticket Button View
# =========================

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction, ticket_type):
        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"{ticket_type}-{user.name}",
            overwrites=overwrites
        )

        await channel.send(f"{user.mention} Welcome to your **{ticket_type}** ticket!")
        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

    @discord.ui.button(label="❤️‍🔥 Editing Help", style=discord.ButtonStyle.primary)
    async def editing(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "editing")

    @discord.ui.button(label="😎 Trading Help", style=discord.ButtonStyle.secondary)
    async def trading(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "trading")

    @discord.ui.button(label="🤓 Staff Complaint", style=discord.ButtonStyle.danger)
    async def staff(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "staff-complaint")

    @discord.ui.button(label="🎉 Giveaway", style=discord.ButtonStyle.success)
    async def giveaway(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "giveaway")


# =========================
# Slash Command
# =========================

@bot.tree.command(name="panel", description="Send the ticket panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Support Ticket Panel",
        description="Click a button below to create a ticket.",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(embed=embed, view=TicketView())


bot.run(os.getenv("TOKEN"))

