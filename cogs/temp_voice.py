import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import config

# --- MODAL PER RINOMINARE ---
class RinominaModal(Modal, title="📝 Rinomina la tua Stanza"):
    nuovo_nome = TextInput(label="Nome Stanza", placeholder="Es: Studio Informatica", min_length=2, max_length=20)
    
    def __init__(self, canale):
        super().__init__()
        self.canale = canale
        
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.canale.edit(name=f"🔊 {self.nuovo_nome.value}")
        await interaction.followup.send(f"✅ Nome cambiato in: {self.nuovo_nome.value}", ephemeral=True)

# --- VIEW DASHBOARD COMPLETA ---
class DashboardFissa(View):
    def __init__(self, cog):
        super().__init__(timeout=None) # Mantiene la dashboard sempre attiva ad ogni riavvio
        self.cog = cog

    async def get_user_channel(self, interaction: discord.Interaction):
        channel_id = self.cog.stanze_attive.get(interaction.user.id)
        
        # Recupero di emergenza se il bot si è riavviato mentre l'utente era in stanza
        if not channel_id and interaction.user.voice and interaction.user.voice.channel:
            possible_chan = interaction.user.voice.channel
            if possible_chan.name.startswith("🔊 Stanza di ") or possible_chan.id in self.cog.stanze_attive.values():
                self.cog.stanze_attive[interaction.user.id] = possible_chan.id
                channel_id = possible_chan.id

        if not channel_id:
            await interaction.followup.send("⚠️ Non hai una stanza attiva gestita da questo pannello! Entra prima nel canale di creazione.", ephemeral=True)
            return None
            
        canale = interaction.guild.get_channel(channel_id)
        if not canale:
            await interaction.followup.send("⚠️ La tua stanza non esiste più o è stata eliminata.", ephemeral=True)
            if interaction.user.id in self.cog.stanze_attive:
                del self.cog.stanze_attive[interaction.user.id]
            return None
            
        return canale

    # --- RIGA 0: ACCESSO E VISIBILITÀ ---
    @discord.ui.button(label="Chiudi", emoji="🔒", style=discord.ButtonStyle.secondary, row=0, custom_id="v_lock")
    async def lock(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            await canale.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.followup.send("Stanza Chiusa! Gli altri utenti non possono più entrare. 🔒", ephemeral=True)

    @discord.ui.button(label="Apri", emoji="🔓", style=discord.ButtonStyle.secondary, row=0, custom_id="v_unlock")
    async def unlock(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            await canale.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.followup.send("Stanza Aperta! Chiunque può connettersi. 🔓", ephemeral=True)

    @discord.ui.button(label="Invisibile", emoji="👻", style=discord.ButtonStyle.secondary, row=0, custom_id="v_hide")
    async def hide(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            await canale.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.followup.send("Stanza ora Invisibile nell'elenco dei canali! 👻", ephemeral=True)

    @discord.ui.button(label="Visibile", emoji="👁️", style=discord.ButtonStyle.secondary, row=0, custom_id="v_show")
    async def show(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            await canale.set_permissions(interaction.guild.default_role, view_channel=True)
            await interaction.followup.send("Stanza ora Visibile a tutti! 👁️", ephemeral=True)

    # --- RIGA 1: PERSONALIZZAZIONE ---
    @discord.ui.button(label="Rinomina", emoji="📝", style=discord.ButtonStyle.primary, row=1, custom_id="v_rename")
    async def rename(self, interaction: discord.Interaction, button: Button):
        # Per i modal non si fa il defer prima, ma controlliamo prima se ha la stanza
        channel_id = self.cog.stanze_attive.get(interaction.user.id)
        if not channel_id and interaction.user.voice and interaction.user.voice.channel:
            possible_chan = interaction.user.voice.channel
            if possible_chan.name.startswith("🔊 Stanza di ") or possible_chan.id in self.cog.stanze_attive.values():
                self.cog.stanze_attive[interaction.user.id] = possible_chan.id
                channel_id = possible_chan.id

        if not channel_id:
            await interaction.response.send_message("⚠️ Non hai una stanza attiva gestita da questo pannello! Entra prima nel canale di creazione.", ephemeral=True)
            return
            
        canale = interaction.guild.get_channel(channel_id)
        if not canale:
            await interaction.response.send_message("⚠️ La tua stanza non esiste più o è stata eliminata.", ephemeral=True)
            return

        await interaction.response.send_modal(RinominaModal(canale))

    @discord.ui.button(label="Limite +", emoji="➕", style=discord.ButtonStyle.success, row=1, custom_id="v_plus")
    async def plus(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            limit = canale.user_limit + 1 if canale.user_limit < 99 else 99
            await canale.edit(user_limit=limit)
            await interaction.followup.send(f"Limite posti aumentato a: {limit}", ephemeral=True)

    @discord.ui.button(label="Limite -", emoji="➖", style=discord.ButtonStyle.success, row=1, custom_id="v_minus")
    async def minus(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            limit = canale.user_limit - 1 if canale.user_limit > 0 else 0
            await canale.edit(user_limit=limit)
            await interaction.followup.send(f"Limite posti diminuito a: {limit}", ephemeral=True)

    # --- RIGA 2: GESTIONE UTENTI E AUDIO ---
    @discord.ui.button(label="Kicka Ultimo", emoji="👞", style=discord.ButtonStyle.danger, row=2, custom_id="v_kick")
    async def kick_last(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            membri = [m for m in canale.members if m.id != interaction.user.id]
            if membri:
                await membri[-1].move_to(None)
                await interaction.followup.send(f"Espulso {membri[-1].display_name} 👞", ephemeral=True)
            else:
                await interaction.followup.send("Nessun utente da cacciare nella stanza!", ephemeral=True)

    @discord.ui.button(label="Qualità Alta", emoji="🔊", style=discord.ButtonStyle.primary, row=2, custom_id="v_bitrate")
    async def high_audio(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            await canale.edit(bitrate=96000)
            await interaction.followup.send("Audio della stanza impostato a 96kbps! 🔊", ephemeral=True)

    @discord.ui.button(label="Svuota", emoji="🧹", style=discord.ButtonStyle.danger, row=2, custom_id="v_clean")
    async def clean_all(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        canale = await self.get_user_channel(interaction)
        if canale:
            for m in canale.members:
                if m.id != interaction.user.id:
                    await m.move_to(None)
            await interaction.followup.send("Stanza svuotata completamente! 🧹", ephemeral=True)

# --- COG ---
class VocaliAvanzati(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stanze_attive = {} 

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(DashboardFissa(self))
        print("🔊 [Vocali] Dashboard fissa registrata in memoria con successo!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == config.VOICE_GENERATOR:
            nuova_stanza = await member.guild.create_voice_channel(
                f"🔊 Stanza di {member.display_name}", 
                category=after.channel.category
            )
            await nuova_stanza.set_permissions(member.guild.default_role, connect=True, view_channel=True)
            await member.move_to(nuova_stanza)
            self.stanze_attive[member.id] = nuova_stanza.id

        if before.channel:
            is_temporary = before.channel.id in self.stanze_attive.values() or before.channel.name.startswith("🔊 Stanza di ")
            
            if is_temporary and len(before.channel.members) == 0:
                owner_id = next((u_id for u_id, c_id in self.stanze_attive.items() if c_id == before.channel.id), None)
                try: 
                    await before.channel.delete()
                except discord.HTTPException: 
                    pass
                
                if owner_id and owner_id in self.stanze_attive: 
                    del self.stanze_attive[owner_id]
                
                if member.id in self.stanze_attive and self.stanze_attive[member.id] == before.channel.id:
                    del self.stanze_attive[member.id]

    @app_commands.command(name="setup_dashboard_vocale", description="Invia la dashboard di gestione canali vocali (Solo Founder)")
    async def setup_dash(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari. Solo il **Founder** può farlo.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎮 INTERFACCIA GESTIONE STANZE VOCALI",
            description=(
                "Benvenuto nel Pannello di Controllo Vocale della classe!\n\n"
                "**ACCESSO E VISIBILITÀ**\n"
                "🔒 `Chiudi` | 🔓 `Apri` | 👻 `Nascondi` | 👁️ `Mostra` \n\n"
                "**PERSONALIZZAZIONE**\n"
                "📝 `Rinomina` | ➕ / ➖ `Posti` \n\n"
                "**GESTIONE UTENTI**\n"
                "👞 `Kicka Ultimo` | 🧹 `Svuota Tutto` | 🔊 `Audio HQ`"
            ),
            color=discord.Color.from_rgb(0, 162, 255)
        )
        embed.set_footer(text="1ªB Informatica • Devi essere dentro la tua stanza per usare i pulsanti.")
        
        await interaction.response.send_message("✅ Dashboard vocale inviata con successo!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=DashboardFissa(self))

async def setup(bot):
    await bot.add_cog(VocaliAvanzati(bot))