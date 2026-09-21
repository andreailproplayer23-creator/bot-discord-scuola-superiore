import discord
from discord.ext import commands
from discord.ui import Button, View
import discord.app_commands
import config
import asyncio

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Il ticket verrà chiuso e cancellato tra 5 secondi...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"[ERRORE] Impossibile eliminare il canale del ticket: {e}")

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apri Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_btn", emoji="🎫")
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        # Controlla se l'utente ha già un ticket aperto cercando nell'ID all'interno del topic
        existing_channel = None
        for channel in guild.text_channels:
            if channel.topic and f"(ID: {member.id})" in channel.topic:
                existing_channel = channel
                break

        if existing_channel:
            await interaction.response.send_message(f"❌ Hai già un ticket aperto: {existing_channel.mention}", ephemeral=True)
            return

        category = guild.get_channel(config.CATEGORY_SUPPORT) or discord.utils.get(guild.categories, name="SUPPORTO")
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        for role_id in [config.ROLE_MOD, config.ROLE_FOUNDER]:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{member.name.lower()}"

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Ticket di supporto aperto da {member.name} (ID: {member.id})"
            )

            embed = discord.Embed(
                title=f"🎫 Ticket di Supporto — {member.name}",
                description=(
                    f"Ciao {member.mention}, benvenuto nel tuo ticket!\n"
                    "Esponi qui sotto il tuo problema o la tua richiesta: lo staff ti risponderà il prima possibile.\n\n"
                    "Quando hai risolto, puoi cliccare sul pulsante **Chiudi Ticket**."
                ),
                color=discord.Color.from_rgb(0, 162, 255)
            )
            embed.set_footer(text="1ªB Informatica • Sistema Ticket")

            await ticket_channel.send(embed=embed, view=CloseTicketView())
            await interaction.response.send_message(f"✅ Il tuo ticket è stato creato con successo: {ticket_channel.mention}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Errore durante la creazione del ticket: {e}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="invioticket", description="Invia il pannello per aprire i ticket di supporto (Solo Founder)")
    async def invioticket(self, interaction: discord.Interaction):
        # Controllo di sicurezza: verifica se l'utente ha il ruolo Founder
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari per usare questo comando. Solo il **Founder** può farlo.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 Assistenza e Supporto - 1ªB Informatica",
            description=(
                "Hai bisogno di aiuto con i compiti, di segnalare un problema o di contattare i moderatori?\n\n"
                "👇 **Clicca sul pulsante qui sotto per aprire un ticket privato con lo staff!**"
            ),
            color=discord.Color.from_rgb(0, 162, 255)
        )
        embed.set_footer(text="1ªB Informatica • Anno Scolastico 2026/2027")

        await interaction.response.send_message("✅ Pannello ticket inviato con successo!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))