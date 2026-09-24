import discord
from discord import app_commands
from discord.ext import commands
import requests
import datetime
import config

class RegistroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _ottieni_dati_classeviva(self):
        if not config.CV_USERNAME or not config.CV_PASSWORD:
            return None, "Credenziali ClasseViva non configurate nel file config.py!"

        try:
            # Endpoint di autenticazione Spaggiari
            auth_url = "https://web.spaggiari.eu/auth/v1/token"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Content-Type": "application/json"
            }
            payload = {
                "uid": config.CV_USERNAME,
                "pwd": config.CV_PASSWORD
            }

            response = requests.post(auth_url, json=payload, headers=headers)
            if response.status_code != 200:
                return None, f"Errore di autenticazione (Codice: {response.status_code})"

            data = response.json()
            token = data.get("token")
            ident = data.get("ident")

            if not token or not ident:
                return None, "Token o Ident non ricevuti da ClasseViva."

            # Imposta le date per oggi e i prossimi 7 giorni
            oggi = datetime.date.today()
            tra_una_settimana = oggi + datetime.timedelta(days=7)
            
            start_str = oggi.strftime("%Y%m%d")
            end_str = tra_una_settimana.strftime("%Y%m%d")

            # Endpoint per l'agenda / compiti
            agenda_url = f"https://web.spaggiari.eu/rest/v1/students/{ident}/agenda/all/{start_str}/{end_str}"
            agenda_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Z-Auth-Token": token,
                "Content-Type": "application/json"
            }

            agenda_resp = requests.get(agenda_url, headers=agenda_headers)
            if agenda_resp.status_code != 200:
                return None, "Impossibile recuperare i dati dell'agenda dal registro."

            agenda_data = agenda_resp.json()
            return agenda_data.get("agenda", []), None

        except Exception as e:
            return None, f"Errore di connessione a ClasseViva: {e}"

    @app_commands.command(name="compiti", description="Visualizza i prossimi compiti e le scadenze da ClasseViva")
    async def compiti(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        # Esegue la richiesta in modo sicuro
        dati_agenda, errore = self._ottieni_dati_classeviva()

        if errore:
            await interaction.followup.send(f"❌ {errore}", ephemeral=True)
            return

        if not dati_agenda:
            await interaction.followup.send("🎉 Ottime notizie! Nessun compito o scadenza registrata nei prossimi giorni.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📚 Registro Elettronico — Compiti & Scadenze",
            description="Ecco gli impegni estratti direttamente da ClasseViva per i prossimi giorni:",
            color=discord.Color.from_rgb(0, 120, 215)
        )

        # Filtra e formatta i primi elementi dell'agenda
        count = 0
        for item in dati_agenda:
            if count >= 8:  # Limita a 8 elementi per evitare embed troppo lunghi
                break
            
            # Tipi comuni in agenda: 1 = Nota/Promemoria, 2 = Compito, 3 = Verifica, ecc.
            titolo = item.get("notes", "Impegno scolastico")
            materia = item.get("authorName", "Materia")
            data_evento = item.get("evtDatetime", "")[:10]
            
            # Formatta la data se presente
            data_formattata = data_evento
            try:
                dt = datetime.datetime.strptime(data_evento, "%Y-%m-%d")
                data_formattata = dt.strftime("%d/%m/%Y")
            except:
                pass

            embed.add_field(
                name=f"📌 {materia} ({data_formattata})",
                value=titolo[:200] if titolo else "Nessun dettaglio aggiuntivo.",
                inline=False
            )
            count += 1

        embed.set_footer(text="1ªB Informatica • ClasseViva Integration")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RegistroCog(bot))