import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import config

class SuggerimentoModal(Modal, title="💡 Invia un Suggerimento / Feedback"):
    titolo_idea = TextInput(label="Titolo / Sintesi della proposta", placeholder="Es: Aggiungere un canale per i progetti", min_length=3, max_length=100, required=True)
    miglioramento = TextInput(label="Cosa vorresti migliorare?", placeholder="Es: L'organizzazione dei ruoli o dei canali...", style=discord.TextStyle.paragraph, min_length=5, max_length=300, required=True)
    note_extra = TextInput(label="Altre idee o richieste (facoltativo)", placeholder="Scrivi qui eventuali dettagli...", style=discord.TextStyle.paragraph, required=False, max_length=300)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        guild = interaction.guild
        channel = guild.get_channel(config.CHANNEL_SUGGESTIONS) # Lo aggiungiamo tra poco o usiamo l'ID diretto

        # 1. Invia un messaggio privato in DM a te (Founder)
        # Troviamo il founder o inviamo direttamente al tuo ID se lo conosciamo, oppure cerchiamo chi ha il ruolo Founder nel server
        try:
            founder_role = guild.get_role(config.ROLE_FOUNDER)
            if founder_role and founder_role.members:
                # Prende il primo membro con il ruolo Founder (tu)
                founder = founder_role.members[0]
                dm_embed = discord.Embed(
                    title="📥 Nuovo Suggerimento Ricevuto!",
                    description=f"Inviato da **{user.display_name}** ({user.mention})",
                    color=discord.Color.from_rgb(0, 162, 255)
                )
                dm_embed.add_field(name="📌 Proposta", value=self.titolo_idea.value, inline=False)
                dm_embed.add_field(name="🛠️ Miglioramento", value=self.miglioramento.value, inline=False)
                if self.note_extra.value:
                    dm_embed.add_field(name="💬 Note Extra", value=self.note_extra.value, inline=False)
                dm_embed.set_footer(text=f"ID Utente: {user.id}")
                
                await founder.send(embed=dm_embed)
        except Exception as e:
            print(f"[ERRORE] Impossibile inviare il DM al Founder: {e}")

        # 2. Aggiorna o invia nel canale dei suggerimenti
        # Cerchiamo l'ultimo messaggio del bot nel canale per aggiornare l'embed cumulativo o ne accodiamo uno
        sug_channel = guild.get_channel(1552039683913941102)
        if sug_channel:
            nuovo_feedback = (
                f"👤 **Utente:** {user.mention} ({user.display_name})\n"
                f"💡 **Proposta:** {self.titolo_idea.value}\n"
                f"🛠️ **Miglioramento:** {self.miglioramento.value}\n"
            )
            if self.note_extra.value:
                nuovo_feedback += f"💬 **Note:** {self.note_extra.value}\n"
            nuovo_feedback += "----------------------------------------"

            # Invia la nuova richiesta come blocco nel canale
            embed_pubblico = discord.Embed(
                title="📥 Nuovo Suggerimento Registrato",
                description=nuovo_feedback,
                color=discord.Color.from_rgb(0, 162, 255)
            )
            embed_pubblico.set_footer(text=f"1ªB Informatica • Sistema Feedback")
            await sug_channel.send(embed=embed_pubblico)

        await interaction.followup.send("✅ Il tuo suggerimento è stato inviato con successo allo staff!", ephemeral=True)

class SuggerimentiView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Invia Suggerimento", style=discord.ButtonStyle.success, custom_id="open_suggerimento_modal", emoji="✍️")
    async def open_modal(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SuggerimentoModal())

class SuggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inviopannellosuggerimenti", description="Invia il pannello dei suggerimenti nel canale dedicato (Solo Founder)")
    async def inviopannellosuggerimenti(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari.", ephemeral=True)
            return

        embed = discord.Embed(
            title="💡 Spazio Suggerimenti e Miglioramenti — 1ªB Informatica",
            description=(
                "Hai un'idea per migliorare il server, aggiungere un canale o segnalare qualcosa?\n\n"
                "👇 **Clicca sul pulsante qui sotto per aprire il modulo e inviare la tua proposta in modo anonimo/diretto allo staff!**"
            ),
            color=discord.Color.from_rgb(0, 162, 255)
        )
        embed.set_footer(text="1ªB Informatica • Anno Scolastico 2026/2027")

        target_channel = interaction.guild.get_channel(1552039683913941102)
        if target_channel:
            await target_channel.send(embed=embed, view=SuggerimentiView())
            await interaction.response.send_message("✅ Pannello suggerimenti inviato nel canale dedicato!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Canale suggerimenti non trovato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))