<<<<<<< HEAD
import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# Configurazione del server Flask per UptimeRobot (mantenimento 24/7)
app = Flask('')

@app.route('/')
def home():
    return "Il bot della 1ªB Informatica è attivo e online 24/7!"

def run():
    # Avvia il server sulla porta 8080 (standard per la maggior parte degli hosting/ambienti)
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Configurazione degli Intents (fondamentali per leggere i messaggi e gestire i membri)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

# Inizializzazione del bot con un prefisso per eventuali comandi testuali
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"-----------------------------------")
    print(f"Bot online come: {bot.user.name}")
    print(f"ID del Bot: {bot.user.id}")
    print(f"-----------------------------------")
    
    # Carica automaticamente tutti i cogs presenti nella cartella cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"[COG] Caricato con successo: {cog_name}")
            except Exception as e:
                print(f"[ERRORE] Impossibile caricare {cog_name}: {e}")

    # Sincronizza i comandi con Discord
    try:
        synced = await bot.tree.sync()
        print(f"[COMANDI] Sincronizzati {len(synced)} comandi slash con successo!")
    except Exception as e:
        print(f"[ERRORE] Sincronizzazione comandi fallita: {e}")
    print(f"-----------------------------------")

# Legge il token in modo sicuro dalle variabili d'ambiente di Render (o dal file .env locale)
TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    # 1. Avvia il server web in background per UptimeRobot
    keep_alive()
    
    # 2. Avvia il bot di Discord
=======
import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# Configurazione del server Flask per UptimeRobot (mantenimento 24/7)
app = Flask('')

@app.route('/')
def home():
    return "Il bot della 1ªB Informatica è attivo e online 24/7!"

def run():
    # Avvia il server sulla porta 8080 (standard per la maggior parte degli hosting/ambienti)
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Configurazione degli Intents (fondamentali per leggere i messaggi e gestire i membri)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

# Inizializzazione del bot con un prefisso per eventuali comandi testuali
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"-----------------------------------")
    print(f"Bot online come: {bot.user.name}")
    print(f"ID del Bot: {bot.user.id}")
    print(f"-----------------------------------")
    
    # Carica automaticamente tutti i cogs presenti nella cartella cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"[COG] Caricato con successo: {cog_name}")
            except Exception as e:
                print(f"[ERRORE] Impossibile caricare {cog_name}: {e}")

    # Sincronizza i comandi con Discord
    try:
        synced = await bot.tree.sync()
        print(f"[COMANDI] Sincronizzati {len(synced)} comandi slash con successo!")
    except Exception as e:
        print(f"[ERRORE] Sincronizzazione comandi fallita: {e}")
    print(f"-----------------------------------")

# Token del tuo bot
TOKEN = "MTU1MTMzNjQzMzIzNzg4NDk1OQ.GZoBmy.TrUFRxbhxb1pcYnV-rWCG6hhwN5c5V3w54Yyv4"

if __name__ == "__main__":
    # 1. Avvia il server web in background per UptimeRobot
    keep_alive()
    
    # 2. Avvia il bot di Discord
>>>>>>> 5fcac0111a5ef290b7d05308e953dee054fbdd66
    bot.run(TOKEN)