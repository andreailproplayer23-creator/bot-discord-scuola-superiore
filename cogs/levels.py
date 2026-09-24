import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import config

LEVELS_PATH = "livelli.json"

# Tabella dei requisiti XP per ogni livello
TABELLA_XP = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
    7: 1350,
    8: 1750,
    9: 2200,
    10: 2700
}

def carica_dati_utenti():
    if not os.path.exists(LEVELS_PATH):
        return {}
    try:
        with open(LEVELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def salva_dati_utenti(dati):
    with open(LEVELS_PATH, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

def calcola_livello(xp):
    livello_attuale = 1
    for lvl, soglia in sorted(TABELLA_XP.items()):
        if xp >= soglia:
            livello_attuale = lvl
        else:
            break
    
    max_livello = max(TABELLA_XP.keys())
    if livello_attuale == max_livello:
        xp_ultimo = TABELLA_XP[max_livello]
        extra_xp = xp - xp_ultimo
        livello_attuale += extra_xp // 600
        
    return livello_attuale

class LevelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def aggiungi_xp(self, guild: discord.Guild, user: discord.User, xp_da_aggiungere: int, channel: discord.abc.Messageable = None):
        dati = carica_dati_utenti()
        user_id = str(user.id)

        if user_id not in dati:
            dati[user_id] = {"xp": 0, "livello": 1}

        vecchio_xp = dati[user_id]["xp"]
        vecchio_livello = calcola_livello(vecchio_xp)

        dati[user_id]["xp"] += xp_da_aggiungere
        nuovo_xp = dati[user_id]["xp"]
        nuovo_livello = calcola_livello(nuovo_xp)

        dati[user_id]["livello"] = nuovo_livello
        salva_dati_utenti(dati)

        if nuovo_livello > vecchio_livello:
            if not channel:
                channel = guild.get_channel(config.CHANNEL_QUIZ)
            
            if channel:
                embed = discord.Embed(
                    title="🎉 LEVEL UP! — 1ªB Informatica",
                    description=f"Complimenti {user.mention}, sei salito di livello!",
                    color=discord.Color.gold()
                )
                if user.avatar:
                    embed.set_thumbnail(url=user.avatar.url)
                
                embed.add_field(name="👤 Utente", value=user.display_name, inline=True)
                embed.add_field(name="⭐ Nuovo Livello", value=f"**Livello {nuovo_livello}**", inline=True)
                embed.add_field(name="📊 XP Totali", value=f"{nuovo_xp} XP", inline=True)
                embed.set_footer(text="Continua a partecipare ai quiz per scalare la classifica!")

                await channel.send(embed=embed)

    @app_commands.command(name="profilo", description="Visualizza il tuo livello, i tuoi XP e la tua scheda personale")
    async def profilo(self, interaction: discord.Interaction, membro: discord.Member = None):
        target = membro or interaction.user
        dati = carica_dati_utenti()
        user_id = str(target.id)

        user_data = dati.get(user_id, {"xp": 0, "livello": 1})
        xp = user_data["xp"]
        livello = user_data["livello"]

        embed = discord.Embed(
            title=f"🛡️ Profilo di {target.display_name}",
            color=discord.Color.from_rgb(0, 162, 255)
        )
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        embed.add_field(name="⭐ Livello", value=str(livello), inline=True)
        embed.add_field(name="✨ Punti ed Esperienza", value=f"{xp} XP", inline=True)
        embed.set_footer(text="1ªB Informatica • Sistema Livelli")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="classifica", description="Visualizza la classifica dei migliori studenti del server")
    async def classifica(self, interaction: discord.Interaction):
        role_founder = interaction.guild.get_role(config.ROLE_FOUNDER)
        is_founder = role_founder and role_founder in interaction.user.roles

        if interaction.channel_id != config.CHANNEL_LEADERBOARD and not is_founder:
            await interaction.response.send_message(f"❌ Questo comando può essere usato solo nel canale <#{config.CHANNEL_LEADERBOARD}>!", ephemeral=True)
            return

        dati = carica_dati_utenti()
        if not dati:
            await interaction.response.send_message("❌ La classifica è ancora vuota! Partecipate ai quiz per guadagnare i primi punti.", ephemeral=True)
            return

        # Ordina gli utenti per XP decrescenti
        utenti_ordinati = sorted(dati.items(), key=lambda x: x[1]["xp"], reverse=True)

        embed = discord.Embed(
            title="🏆 Classifica Ufficiale — 1ªB Informatica",
            description="I migliori studenti del server in base ai punti accumulati nei quiz:",
            color=discord.Color.from_rgb(255, 215, 0)
        )

        medaglie = ["🥇", "🥈", "🥉"]

        descrizione_classifica = ""
        for i, (user_id, info) in enumerate(utenti_ordinati[:10]): # Prende i primi 10
            member = interaction.guild.get_member(int(user_id))
            nome_utente = member.display_name if member else f"Utente ({user_id})"
            
            simbolo = medaglie[i] if i < 3 else f"`#{i+1}`"
            descrizione_classifica += f"{simbolo} **{nome_utente}** — Livello {info['livello']} (*{info['xp']} XP*)\n"

        embed.add_field(name="Top Studenti", value=descrizione_classifica or "Nessun dato disponibile.", inline=False)
        embed.set_footer(text="1ªB Informatica • Continua a giocare per salire sul podio!")

        if interaction.channel_id == config.CHANNEL_LEADERBOARD:
            await interaction.response.send_message(embed=embed)
        else:
            channel = interaction.guild.get_channel(config.CHANNEL_LEADERBOARD)
            if channel:
                await channel.send(embed=embed)
                await interaction.response.send_message("✅ Classifica inviata nel canale dedicato!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canale classifica non trovato nel config!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LevelsCog(bot))