<<<<<<< HEAD
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, Select, View
import config

# Dizionario temporaneo per memorizzare le verifiche inviate (chiave: message_id, valore: dettagli)
VERIFICHE_ATTIVE = {}

# --- MODAL PER INSERIRE LA VERIFICA ---
class AggiungiVerificaModal(Modal, title="📚 Aggiungi Verifica o Compito"):
    materia = TextInput(label="Materia", placeholder="Es: Informatica, Matematica...", min_length=2, max_length=50, required=True)
    argomento = TextInput(label="Argomento / Capitolo", placeholder="Es: Funzioni in Python", min_length=3, max_length=100, required=True)
    data = TextInput(label="Data della Verifica", placeholder="Es: Lunedì 28 Settembre / 28/09/2026", min_length=5, max_length=30, required=True)
    note = TextInput(label="Note aggiuntive (facoltativo)", placeholder="Es: Portare il libro...", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🚨 NUOVA VERIFICA / COMPITO IN ARRIVO!",
            color=discord.Color.from_rgb(255, 69, 58)
        )
        embed.add_field(name="📖 Materia", value=self.materia.value, inline=False)
        embed.add_field(name="📌 Argomento", value=self.argomento.value, inline=False)
        embed.add_field(name="📅 Data", value=self.data.value, inline=False)
        
        if self.note.value:
            embed.add_field(name="💬 Note", value=self.note.value, inline=False)
            
        embed.set_footer(text=f"Inserito da {interaction.user.display_name} • 1ªB Informatica")

        # Invia il messaggio nel canale in cui è stato eseguito il comando
        messaggio = await self.channel.send(embed=embed)
        
        # Salviamo il messaggio nel dizionario per poterlo eliminare in seguito
        VERIFICHE_ATTIVE[messaggio.id] = {
            "titolo": f"{self.materia.value} - {self.data.value}",
            "message_id": messaggio.id,
            "channel_id": self.channel.id
        }

        await interaction.followup.send("✅ Verifica pubblicata con successo in questo canale!", ephemeral=True)

# --- MENU A TENDINA PER ELIMINARE LE VERIFICHE ---
class SelectEliminaVerifica(Select):
    def __init__(self):
        options = []
        # Prendiamo le ultime 25 verifiche inserite (limite massimo di Discord per i menu)
        for msg_id, info in list(VERIFICHE_ATTIVE.items())[-25:]:
            options.append(discord.SelectOption(
                label=info["titolo"][:100], 
                value=str(msg_id),
                description="Clicca per eliminare questo compito/verifica"
            ))
            
        super().__init__(placeholder="Seleziona la verifica da eliminare...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        msg_id = int(self.values[0])
        info = VERIFICHE_ATTIVE.get(msg_id)
        
        if info:
            try:
                channel = interaction.guild.get_channel(info["channel_id"])
                if channel:
                    msg = await channel.fetch_message(info["message_id"])
                    await msg.delete()
            except discord.HTTPException:
                pass
            
            # Rimuoviamo dal dizionario
            if msg_id in VERIFICHE_ATTIVE:
                del VERIFICHE_ATTIVE[msg_id]
                
            await interaction.followup.send("🗑️ Verifica eliminata con successo!", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ Verifica non trovata o già eliminata.", ephemeral=True)

class ViewEliminaVerifica(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(SelectEliminaVerifica())

# --- COG ---
class VerificheCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aggiungi_verifica", description="Apre il modulo per aggiungere una verifica in questo canale (Solo Founder)")
    async def aggiungi_verifica(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari. Solo il **Founder** può farlo.", ephemeral=True)
            return

        # Apre il modale usando direttamente il canale attuale dell'interazione
        await interaction.response.send_modal(AggiungiVerificaModal(interaction.channel))

    @app_commands.command(name="elimina_verifica", description="Mostra l'elenco delle verifiche per eliminarne una (Solo Founder)")
    async def elimina_verifica(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari. Solo il **Founder** può farlo.", ephemeral=True)
            return

        if not VERIFICHE_ATTIVE:
            await interaction.response.send_message("ℹ️ Non ci sono verifiche registrate in memoria da eliminare.", ephemeral=True)
            return

        await interaction.response.send_message("Seleziona dal menu sottostante la verifica o il compito da rimuovere:", view=ViewEliminaVerifica(), ephemeral=True)

async def setup(bot):
=======
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, Select, View
import config

# Dizionario temporaneo per memorizzare le verifiche inviate (chiave: message_id, valore: dettagli)
VERIFICHE_ATTIVE = {}

# --- MODAL PER INSERIRE LA VERIFICA ---
class AggiungiVerificaModal(Modal, title="📚 Aggiungi Verifica o Compito"):
    materia = TextInput(label="Materia", placeholder="Es: Informatica, Matematica...", min_length=2, max_length=50, required=True)
    argomento = TextInput(label="Argomento / Capitolo", placeholder="Es: Funzioni in Python", min_length=3, max_length=100, required=True)
    data = TextInput(label="Data della Verifica", placeholder="Es: Lunedì 28 Settembre / 28/09/2026", min_length=5, max_length=30, required=True)
    note = TextInput(label="Note aggiuntive (facoltativo)", placeholder="Es: Portare il libro...", style=discord.TextStyle.paragraph, required=False, max_length=300)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🚨 NUOVA VERIFICA / COMPITO IN ARRIVO!",
            color=discord.Color.from_rgb(255, 69, 58)
        )
        embed.add_field(name="📖 Materia", value=self.materia.value, inline=False)
        embed.add_field(name="📌 Argomento", value=self.argomento.value, inline=False)
        embed.add_field(name="📅 Data", value=self.data.value, inline=False)
        
        if self.note.value:
            embed.add_field(name="💬 Note", value=self.note.value, inline=False)
            
        embed.set_footer(text=f"Inserito da {interaction.user.display_name} • 1ªB Informatica")

        # Invia il messaggio nel canale in cui è stato eseguito il comando
        messaggio = await self.channel.send(embed=embed)
        
        # Salviamo il messaggio nel dizionario per poterlo eliminare in seguito
        VERIFICHE_ATTIVE[messaggio.id] = {
            "titolo": f"{self.materia.value} - {self.data.value}",
            "message_id": messaggio.id,
            "channel_id": self.channel.id
        }

        await interaction.followup.send("✅ Verifica pubblicata con successo in questo canale!", ephemeral=True)

# --- MENU A TENDINA PER ELIMINARE LE VERIFICHE ---
class SelectEliminaVerifica(Select):
    def __init__(self):
        options = []
        # Prendiamo le ultime 25 verifiche inserite (limite massimo di Discord per i menu)
        for msg_id, info in list(VERIFICHE_ATTIVE.items())[-25:]:
            options.append(discord.SelectOption(
                label=info["titolo"][:100], 
                value=str(msg_id),
                description="Clicca per eliminare questo compito/verifica"
            ))
            
        super().__init__(placeholder="Seleziona la verifica da eliminare...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        msg_id = int(self.values[0])
        info = VERIFICHE_ATTIVE.get(msg_id)
        
        if info:
            try:
                channel = interaction.guild.get_channel(info["channel_id"])
                if channel:
                    msg = await channel.fetch_message(info["message_id"])
                    await msg.delete()
            except discord.HTTPException:
                pass
            
            # Rimuoviamo dal dizionario
            if msg_id in VERIFICHE_ATTIVE:
                del VERIFICHE_ATTIVE[msg_id]
                
            await interaction.followup.send("🗑️ Verifica eliminata con successo!", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ Verifica non trovata o già eliminata.", ephemeral=True)

class ViewEliminaVerifica(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(SelectEliminaVerifica())

# --- COG ---
class VerificheCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aggiungi_verifica", description="Apre il modulo per aggiungere una verifica in questo canale (Solo Founder)")
    async def aggiungi_verifica(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari. Solo il **Founder** può farlo.", ephemeral=True)
            return

        # Apre il modale usando direttamente il canale attuale dell'interazione
        await interaction.response.send_modal(AggiungiVerificaModal(interaction.channel))

    @app_commands.command(name="elimina_verifica", description="Mostra l'elenco delle verifiche per eliminarne una (Solo Founder)")
    async def elimina_verifica(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari. Solo il **Founder** può farlo.", ephemeral=True)
            return

        if not VERIFICHE_ATTIVE:
            await interaction.response.send_message("ℹ️ Non ci sono verifiche registrate in memoria da eliminare.", ephemeral=True)
            return

        await interaction.response.send_message("Seleziona dal menu sottostante la verifica o il compito da rimuovere:", view=ViewEliminaVerifica(), ephemeral=True)

async def setup(bot):
>>>>>>> 5fcac0111a5ef290b7d05308e953dee054fbdd66
    await bot.add_cog(VerificheCog(bot))