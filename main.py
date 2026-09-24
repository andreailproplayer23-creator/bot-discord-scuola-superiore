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

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.guild_id = discord.Object(id=1551330601079021719)

    async def setup_hook(self):
        print("-----------------------------------")
        print("[SETUP] Avvio caricamento moduli (Cogs)...")
        
        # Caricamento esplicito di tutti i cogs
        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    cog_name = filename[:-3]
                    try:
                        await self.load_extension(f"cogs.{cog_name}")
                        print(f"[COG] Caricato con successo: {cog_name}")
                    except Exception as e:
                        print(f"[ERRORE GRAVE] Impossibile caricare {cog_name}: {e}")
        
        # Registrazione delle viste persistenti
        try:
            self.add_view(SuggerimentiView())
            self.add_view(FattoView())
            print("[VIEWS] Viste persistenti registrate con successo!")
        except Exception as e:
            print(f"[ERRORE] Impossibile registrare le viste persistenti: {e}")

        # Sincronizzazione dei comandi sulla gilda specifica
        try:
            self.tree.copy_global_to(guild=self.guild_id)
            synced = await self.tree.sync(guild=self.guild_id)
            print(f"[COMANDI] Sincronizzati {len(synced)} comandi sul server 1ªB Informatica!")
        except Exception as e:
            print(f"[ERRORE] Sincronizzazione comandi fallita: {e}")
        print("-----------------------------------")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"[ONLINE] Bot connesso come: {bot.user.name} (ID: {bot.user.id})")

TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)