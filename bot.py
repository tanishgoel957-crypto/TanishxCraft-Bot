import discord
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True

GUILD_ID = 1439766744758489111
STAFF_ROLE_ID = 1439766745153011771
CATEGORY_ID = 1466623583823597701
LOG_CHANNEL_ID = 1478235523851227246


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
# Close Ticket Button
# =========================

class CloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):

        # Only staff can close
        if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "❌ Only staff can close tickets.",
                ephemeral=True
            )
            return

        channel = interaction.channel
        messages = []

        async for msg in channel.history(limit=None, oldest_first=True):
            messages.append(f"{msg.author}: {msg.content}")

        transcript = "\n".join(messages)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            file = discord.File(
                fp=bytes(transcript, "utf-8"),
                filename=f"{channel.name}-transcript.txt"
            )
            await log_channel.send(
                content=f"📄 Transcript for {channel.name}",
                file=file
            )

        await channel.delete()


# =========================
# Ticket Creation
# =========================

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction, ticket_type):
        guild = interaction.guild
        user = interaction.user

        # Prevent duplicate tickets
        for channel in guild.text_channels:
            if channel.name == f"{ticket_type}-{user.name}":
                await interaction.response.send_message(
                    "❌ You already have an open ticket.",
                    ephemeral=True
                )
                return

        category = guild.get_channel(CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"{ticket_type}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{ticket_type.title()} Ticket",
            description="Support will be with you shortly.",
            color=discord.Color.blurple()
        )

        embed.set_image(url="https://i.imgur.com/4M34hi2.png")

        await channel.send(
            content=f"{user.mention} {staff_role.mention}",
            embed=embed,
            view=CloseView()
        )

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
# Panel Command
# =========================

@bot.tree.command(name="panel", description="Send the ticket panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ Support Ticket Panel",
        description="Click a button below to create a ticket.",
        color=discord.Color.blurple()
    )

    embed.set_image(url="https://i.imgur.com/4M34hi2.png")

    await interaction.response.send_message(embed=embed, view=TicketView())


bot.run(os.getenv("TOKEN"))

