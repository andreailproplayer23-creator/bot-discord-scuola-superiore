import discord
from discord.ext import commands, tasks
import datetime
import config

class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_dashboard.start()

    def cog_unload(self):
        self.update_dashboard.cancel()

    async def get_or_create_dashboard_message(self, channel):
        # Cerca negli ultimi messaggi del canale se il bot ha già inviato una dashboard
        async for message in channel.history(limit=10):
            if message.author == self.bot.user and message.embeds:
                return message
        return None

    @tasks.loop(seconds=5)
    async def update_dashboard(self):
        channel = self.bot.get_channel(config.CHANNEL_DASHBOARD)
        if not channel:
            return

        guild = channel.guild
        if not guild:
            return

        # Calcolo statistiche dinamiche
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        
        # Creazione dell'embed aggiornato
        embed = discord.Embed(
            title="📊 Dashboard Live • 1ªB Informatica",
            description="Panoramica in tempo reale dello stato del server. Questo pannello si aggiorna automaticamente ogni 5 secondi.",
            color=discord.Color.from_rgb(0, 162, 232),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="👥 Membri",
            value=f"• Totale: **{total_members}**\n• Online stimati: **{online_members}**",
            inline=True
        )

        embed.add_field(
            name="🤖 Stato Bot",
            value="• Ping: **{0}ms**\n• Versione: **Render Live**".format(round(self.bot.latency * 1000)),
            inline=True
        )

        embed.add_field(
            name="📌 Collegamenti Rapidi",
            value="Usa i comandi slash (`/`) per interagire con i quiz, i ticket e i suggerimenti nel server!",
            inline=False
        )

        embed.set_footer(text="Ultimo aggiornamento automatico")

        try:
            # Cerca il messaggio esistente nel canale
            message = await self.get_or_create_dashboard_message(channel)
            if message:
                # Modifica il messaggio esistente senza spammare la chat
                await message.edit(embed=embed)
            else:
                # Se non esiste ancora, ne crea uno nuovo
                await channel.send(embed=embed)
        except Exception as e:
            print(f"[ERRORE DASHBOARD]: {e}")

    @update_dashboard.before_loop
    async def before_update_dashboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DashboardCog(bot))