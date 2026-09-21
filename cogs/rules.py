<<<<<<< HEAD
import discord
from discord.ext import commands
from discord.ui import Button, View
import discord.app_commands
import config

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accetta le regole", style=discord.ButtonStyle.green, custom_id="accept_rules_btn", emoji="✅")
    async def accept_rules(self, interaction: discord.Interaction, button: Button):
        # 1. Diciamo subito a Discord di mettersi in attesa (impedisce il timeout di 3 secondi)
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        role_guest = guild.get_role(config.ROLE_GUEST)
        role_student = guild.get_role(config.ROLE_STUDENT)

        if not role_guest or not role_student:
            await interaction.followup.send("❌ Errore: I ruoli configurati non esistono sul server!", ephemeral=True)
            return

        member = interaction.user

        if role_student in member.roles:
            await interaction.followup.send("Sei già verificato e hai già il ruolo di Studente!", ephemeral=True)
            return

        try:
            if role_guest in member.roles:
                await member.remove_roles(role_guest)
            await member.add_roles(role_student)
            
            await interaction.followup.send("🎉 **Verifica completata con successo!** Benvenuto nella 1ªB Informatica.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Errore durante l'assegnazione dei ruoli: {e}", ephemeral=True)

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="invioregole", description="Invia il pannello delle regole con il pulsante di verifica (Solo Founder)")
    async def invioregole(self, interaction: discord.Interaction):
        # Controllo di sicurezza: verifica se l'utente ha il ruolo Founder
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari per usare questo comando. Solo il **Founder** può farlo.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📜 Regolamento Ufficiale - 1ªB Informatica",
            description=(
                "Benvenuto nel server ufficiale della classe! Per mantenere un ambiente "
                "ordinato, rispettoso e utile per la scuola, ti chiediamo di seguire poche semplici regole:\n\n"
                "1️⃣ **Rispetto reciproco:** Niente insulti, discriminazioni o comportamenti tossici.\n"
                "2️⃣ **Canali appropriati:** Usa i canali corretti (es. niente meme nella chat di studio).\n"
                "3️⃣ **No Spam:** Evita invii massicci di messaggi o link non pertinenti.\n"
                "4️⃣ **Ambiente scolastico:** Ricorda che questo è un supporto per la classe.\n\n"
                "👇 **Clicca sul pulsante qui sotto per accettare le regole e sbloccare il server!**"
            ),
            color=discord.Color.from_rgb(0, 255, 200)
        )
        embed.set_footer(text="1ªB Informatica • Anno Scolastico 2026/2027")

        # Risponde al comando in modo nascosto ed invia l'embed nel canale
        await interaction.response.send_message("✅ Pannello regole inviato con successo!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=VerificationView())

async def setup(bot):
=======
import discord
from discord.ext import commands
from discord.ui import Button, View
import discord.app_commands
import config

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accetta le regole", style=discord.ButtonStyle.green, custom_id="accept_rules_btn", emoji="✅")
    async def accept_rules(self, interaction: discord.Interaction, button: Button):
        # 1. Diciamo subito a Discord di mettersi in attesa (impedisce il timeout di 3 secondi)
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        role_guest = guild.get_role(config.ROLE_GUEST)
        role_student = guild.get_role(config.ROLE_STUDENT)

        if not role_guest or not role_student:
            await interaction.followup.send("❌ Errore: I ruoli configurati non esistono sul server!", ephemeral=True)
            return

        member = interaction.user

        if role_student in member.roles:
            await interaction.followup.send("Sei già verificato e hai già il ruolo di Studente!", ephemeral=True)
            return

        try:
            if role_guest in member.roles:
                await member.remove_roles(role_guest)
            await member.add_roles(role_student)
            
            await interaction.followup.send("🎉 **Verifica completata con successo!** Benvenuto nella 1ªB Informatica.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Errore durante l'assegnazione dei ruoli: {e}", ephemeral=True)

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="invioregole", description="Invia il pannello delle regole con il pulsante di verifica (Solo Founder)")
    async def invioregole(self, interaction: discord.Interaction):
        # Controllo di sicurezza: verifica se l'utente ha il ruolo Founder
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        if not role_founder or role_founder not in interaction.user.roles:
            await interaction.response.send_message("❌ Non hai i permessi necessari per usare questo comando. Solo il **Founder** può farlo.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📜 Regolamento Ufficiale - 1ªB Informatica",
            description=(
                "Benvenuto nel server ufficiale della classe! Per mantenere un ambiente "
                "ordinato, rispettoso e utile per la scuola, ti chiediamo di seguire poche semplici regole:\n\n"
                "1️⃣ **Rispetto reciproco:** Niente insulti, discriminazioni o comportamenti tossici.\n"
                "2️⃣ **Canali appropriati:** Usa i canali corretti (es. niente meme nella chat di studio).\n"
                "3️⃣ **No Spam:** Evita invii massicci di messaggi o link non pertinenti.\n"
                "4️⃣ **Ambiente scolastico:** Ricorda che questo è un supporto per la classe.\n\n"
                "👇 **Clicca sul pulsante qui sotto per accettare le regole e sbloccare il server!**"
            ),
            color=discord.Color.from_rgb(0, 255, 200)
        )
        embed.set_footer(text="1ªB Informatica • Anno Scolastico 2026/2027")

        # Risponde al comando in modo nascosto ed invia l'embed nel canale
        await interaction.response.send_message("✅ Pannello regole inviato con successo!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=VerificationView())

async def setup(bot):
>>>>>>> 5fcac0111a5ef290b7d05308e953dee054fbdd66
    await bot.add_cog(Rules(bot))