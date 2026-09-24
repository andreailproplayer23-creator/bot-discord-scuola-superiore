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

        # Statistiche dettagliate della gilda
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        bots_count = sum(1 for m in guild.members if m.bot)
        humans_count = total_members - bots_count
        
        total_channels = len(guild.channels)
        total_roles = len(guild.roles)
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        # Creazione dell'embed super dettagliato
        embed = discord.Embed(
            title="📊 Dashboard Live • 1ªB Informatica",
            description="Panoramica completa in tempo reale dello stato del server. Si aggiorna automaticamente ogni 5 secondi.",
            color=discord.Color.from_rgb(0, 162, 232),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="👥 Utenti & Bot",
            value=f"• Umani: **{humans_count}**\n• Bot: **{bots_count}**\n• Online: **{online_members}**",
            inline=True
        )

        embed.add_field(
            name="⚙️ Struttura Server",
            value=f"• Canali: **{total_channels}**\n• Ruoli: **{total_roles}**\n• Livello Boost: **Liv. {boost_level}** ({boost_count} boost)",
            inline=True
        )

        embed.add_field(
            name="🤖 Stato Bot",
            value=f"• Ping: **{round(self.bot.latency * 1000)}ms**\n• Host: **Render**\n• Stato: **Online 24/7**",
            inline=True
        )

        embed.add_field(
            name="📌 Collegamenti Rapidi",
            value="Usa i comandi ` / ` per interagire con i quiz, i ticket e i suggerimenti!",
            inline=False
        )

        embed.set_footer(text=f"Server ID: {guild.id} • Ultimo aggiornamento")

        try:
            message = await self.get_or_create_dashboard_message(channel)
            if message:
                await message.edit(embed=embed)
            else:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"[ERRORE DASHBOARD]: {e}")

    @update_dashboard.before_loop
    async def before_update_dashboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DashboardCog(bot))