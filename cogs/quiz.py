import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
import random
import json
import os
import config

JSON_PATH = "domande.json"

def carica_domande():
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRORE] Impossibile leggere {JSON_PATH}: {e}")
        return []

class QuizButton(Button):
    def __init__(self, label: str, is_correct: bool):
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.is_correct = is_correct

    async def callback(self, interaction: discord.Interaction):
        for child in self.view.children:
            child.disabled = True
            if child.is_correct:
                child.style = discord.ButtonStyle.success
            elif child == self:
                child.style = discord.ButtonStyle.danger

        if self.is_correct:
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.green()
            embed.add_field(name="Risultato", value=f"✅ Risposta corretta da {interaction.user.mention}! Ottimo lavoro! (+50 XP)", inline=False)
            await interaction.response.edit_message(embed=embed, view=self.view)

            # Assegna XP tramite il cog dei livelli se disponibile
            levels_cog = interaction.client.get_cog("LevelsCog")
            if levels_cog:
                await levels_cog.aggiungi_xp(
                    guild=interaction.guild,
                    user=interaction.user,
                    xp_da_aggiungere=50,
                    channel=interaction.channel
                )
        else:
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.red()
            embed.add_field(name="Risultato", value=f"❌ Risposta errata, {interaction.user.mention}. La risposta corretta era un'altra!", inline=False)
            await interaction.response.edit_message(embed=embed, view=self.view)

class QuizView(View):
    def __init__(self, opzioni, risposta_corretta):
        super().__init__(timeout=30)
        random.shuffle(opzioni)
        for opzione in opzioni:
            is_correct = (opzione == risposta_corretta)
            self.add_item(QuizButton(label=opzione, is_correct=is_correct))

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quiz", description="Avvia una domanda di quiz informatico dal database JSON")
    async def quiz(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        is_founder = role_founder and role_founder in interaction.user.roles

        if interaction.channel_id != config.CHANNEL_QUIZ and not is_founder:
            await interaction.response.send_message(f"❌ Questo comando può essere usato solo nel canale <#{config.CHANNEL_QUIZ}>!", ephemeral=True)
            return

        lista_domande = carica_domande()
        if not lista_domande:
            await interaction.response.send_message("❌ Il database delle domande (`domande.json`) è vuoto o non è stato trovato!", ephemeral=True)
            return

        q = random.choice(lista_domande)

        embed = discord.Embed(
            title="🧠 Quiz di Informatica — 1ªB Informatica",
            description=f"**{q['domanda']}**",
            color=discord.Color.from_rgb(0, 162, 255)
        )
        embed.set_footer(text=f"Richiesto da {interaction.user.display_name} • Hai 30 secondi per rispondere!")

        view = QuizView(q['opzioni'], q['risposta_corretta'])

        if interaction.channel_id == config.CHANNEL_QUIZ:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            channel = interaction.guild.get_channel(config.CHANNEL_QUIZ)
            if channel:
                await channel.send(embed=embed, view=view)
                await interaction.response.send_message("✅ Domanda del quiz avviata nel canale dedicato!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canale quiz non trovato nel config!", ephemeral=True)

    # Ascolta i messaggi privati (DM) per aggiornare il file JSON automaticamente
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel) and message.attachments:
            guild = self.bot.get_guild(1551330601079021719)
            if not guild:
                guild = list(self.bot.guilds)[0] if self.bot.guilds else None
            
            is_founder = False
            if guild:
                member = guild.get_member(message.author.id)
                if member:
                    role_founder = guild.get_role(config.ROLE_FOUNDER)
                    if role_founder and role_founder in member.roles:
                        is_founder = True

            if not is_founder:
                await message.reply("❌ Non hai i permessi necessari per aggiornare il database delle domande.")
                return

            for attachment in message.attachments:
                if attachment.filename.endswith(".json"):
                    try:
                        file_bytes = await attachment.read()
                        dati_json = json.loads(file_bytes.decode("utf-8"))
                        
                        if not isinstance(dati_json, list):
                            await message.reply("❌ Il file JSON deve contenere una lista di domande.")
                            return

                        with open(JSON_PATH, "w", encoding="utf-8") as f:
                            json.dump(dati_json, f, indent=4, ensure_ascii=False)

                        await message.reply(f"✅ **Database aggiornato con successo!** Caricate {len(dati_json)} domande dal file `{attachment.filename}`.")
                    except json.JSONDecodeError:
                        await message.reply("❌ Errore: Il file inviato non è un JSON valido.")
                    except Exception as e:
                        await message.reply(f"❌ Errore durante il salvataggio del file: {e}")

async def setup(bot):
    await bot.add_cog(QuizCog(bot))