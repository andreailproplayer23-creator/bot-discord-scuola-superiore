import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# Importiamo le viste dai cogs per renderle persistenti
from cogs.suggestions import SuggerimentiView, FattoView
# Se hai altre View persistenti (es. Ticket o Verifiche), puoi importarle qui sotto:
# from cogs.tickets import TicketView

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

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.guild_id = discord.Object(id=1551330601079021719)

    async def setup_hook(self):
        print(f"-----------------------------------")
        print(f"[AVVIO] Caricamento dei Cogs in corso...")
        
        # Carica automaticamente tutti i cogs presenti nella cartella cogs prima dell'avvio
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    print(f"[COG] Caricato con successo: {cog_name}")
                except Exception as e:
                    print(f"[ERRORE] Impossibile caricare {cog_name}: {e}")

        # REGISTRAZIONE DELLE VIEW PERSISTENTI (Impedisce che i bottoni scadano al riavvio)
        try:
            self.add_view(SuggerimentiView())
            self.add_view(FattoView())
            print("[VIEWS] Viste persistenti registrate con successo!")
        except Exception as e:
            print(f"[ERRORE] Impossibile registrare le viste persistenti: {e}")
        print(f"-----------------------------------")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"-----------------------------------")
    print(f"Bot online come: {bot.user.name}")
    print(f"ID del Bot: {bot.user.id}")
    print(f"-----------------------------------")
    
    # Sincronizza i comandi istantaneamente sul server specifico ora che i cogs sono pronti
    try:
        bot.tree.copy_global_to(guild=bot.guild_id)
        synced = await bot.tree.sync(guild=bot.guild_id)
        print(f"[COMANDI] Sincronizzati {len(synced)} comandi sul server 1ªB Informatica!")
    except Exception as e:
        print(f"[ERRORE] Sincronizzazione comandi fallita: {e}")
    print(f"-----------------------------------")

TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)