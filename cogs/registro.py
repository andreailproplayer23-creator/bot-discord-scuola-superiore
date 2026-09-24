import discord
from discord.ext import commands
from discord import app_commands
import datetime

class RegistroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="compiti", description="Visualizza i compiti e le scadenze da ClasseViva")
    async def compiti(self, interaction: discord.Interaction):
        # Mettiamo un defer per evitare che la richiesta scada mentre interroga l'API
        await interaction.response.defer(thinking=True)

        try:
            # --- INSERISCI QUI LA TUA LOGICA CLASSEVIVA ---
            # Esempio di embed temporaneo per verificare che il comando risponda
            embed = discord.Embed(
                title="📚 Registro Elettronico – Compiti & Scadenze",
                description="Ecco gli impegni estratti direttamente da ClasseViva per i prossimi giorni:",
                color=discord.Color.from_rgb(0, 120, 215)
            )
            
            # Esempio di campo (puoi sostituirlo con i dati veri della tua API)
            embed.add_field(
                name="📌 Esempio Materia (Data)",
                value="Questo è un test di collegamento con ClasseViva.",
                inline=False
            )
            
            embed.set_footer(text="1ªB Informatica • ClasseViva Integration")
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Errore durante il recupero dei dati da ClasseViva: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RegistroCog(bot))