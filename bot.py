import discord
from discord import app_commands
from discord.ui import View, Select
import os

intents = discord.Intents.default()
intents.message_content = True

GUILD_ID = 1439766744758489111  # keep your guild ID here


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
# Ticket Dropdown
# =========================

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Editing Help", emoji="❤️‍🔥", description="Need editing support"),
            discord.SelectOption(label="Trading Help", emoji="😎", description="Trading issues"),
            discord.SelectOption(label="Staff Complaint", emoji="🤓", description="Report staff"),
            discord.SelectOption(label="Giveaway", emoji="🎉", description="Giveaway questions")
        ]

        super().__init__(
            placeholder="Select ticket type...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        ticket_type = self.values[0]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"{ticket_type.lower().replace(' ', '-')}-{user.name}",
            overwrites=overwrites
        )

        await channel.send(f"{user.mention} Welcome! This is your **{ticket_type}** ticket.")
        await interaction.response.send_message(
            f"✅ Your **{ticket_type}** ticket has been created: {channel.mention}",
            ephemeral=True
        )


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# =========================
# Slash Command
# =========================

@bot.tree.command(name="panel", description="Open the ticket panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Support Ticket Panel",
        description="Select the type of ticket you want to create.",
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())


bot.run(os.getenv("TOKEN"))

