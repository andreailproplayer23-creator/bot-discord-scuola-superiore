import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# Importiamo le viste dai cogs per renderle persistenti
from cogs.suggestions import SuggerimentiView, FattoView

# Configurazione del server Flask per UptimeRobot (mantenimento 24/7)
app = Flask('')

@app.route('/')
def home():
    return "Il bot della 1ªB Informatica è attivo e online 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Configurazione degli Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
GUILD_ID = discord.Object(id=1551330601079021719)

@bot.event
async def on_ready():
    print("-----------------------------------")
    print(f"[AVVIO] Bot connesso come: {bot.user.name}")
    
    # Caricamento esplicito dei Cogs
    if os.path.exists("./cogs"):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = filename[:-3]
                try:
                    await bot.load_extension(f"cogs.{cog_name}")
                    print(f"[COG] Caricato con successo: {cog_name}")
                except Exception as e:
                    print(f"[ERRORE] Impossibile caricare {cog_name}: {e}")

    # Registrazione delle viste persistenti
    try:
        bot.add_view(SuggerimentiView())
        bot.add_view(FattoView())
        print("[VIEWS] Viste persistenti registrate con successo!")
    except Exception as e:
        print(f"[ERRORE] Impossibile registrare le viste persistenti: {e}")

    # Sincronizzazione dei comandi sul server
    try:
        bot.tree.copy_global_to(guild=GUILD_ID)
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"[COMANDI] Sincronizzati {len(synced)} comandi sul server 1ªB Informatica!")
    except Exception as e:
        print(f"[ERRORE] Sincronizzazione comandi fallita: {e}")
    print("-----------------------------------")

TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)