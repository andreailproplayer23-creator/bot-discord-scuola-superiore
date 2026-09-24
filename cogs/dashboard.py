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

        # --- RACCOLTA DATI AVANZATA (10+ INFORMAZIONI) ---
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        bots_count = sum(1 for m in guild.members if m.bot)
        humans_count = total_members - bots_count
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        total_roles = len(guild.roles)
        
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        owner = guild.owner.name if guild.owner else "Sconosciuto"
        
        # Data di creazione del server formattata
        created_at = guild.created_at.strftime("%d/%m/%Y")
        
        # Conteggio emoji e sticker
        emojis_count = len(guild.emojis)
        stickers_count = len(guild.stickers)
        
        # Creazione dell'embed con le nuove categorie
        embed = discord.Embed(
            title="📊 Dashboard Live Ufficiale • 1ªB Informatica",
            description="Panoramica dettagliata in tempo reale dello stato del server. Aggiornamento automatico ogni 5s.",
            color=discord.Color.from_rgb(0, 162, 232),
            timestamp=datetime.datetime.now()
        )

        # 1. Utenti & Presenze
        embed.add_field(
            name="👥 Utenti",
            value=f"• Totale: **{total_members}**\n• Umani: **{humans_count}**\n• Bot: **{bots_count}**\n• Online: **{online_members}**",
            inline=True
        )

        # 2. Canali & Categorie
        embed.add_field(
            name="📁 Canali",
            value=f"• Testuali: **{text_channels}**\n• Vocali: **{voice_channels}**\n• Categorie: **{categories}**\n• Ruoli: **{total_roles}**",
            inline=True
        )

        # 3. Server Info & Boost
        embed.add_field(
            name="⚡ Community",
            value=f"• Owner: **{owner}**\n• Creato il: **{created_at}**\n• Liv. Boost: **Liv. {boost_level}** ({boost_count})",
            inline=True
        )

        # 4. Risorse & Extra
        embed.add_field(
            name="🎨 Risorse",
            value=f"• Emoji: **{emojis_count}**\n• Sticker: **{stickers_count}**",
            inline=True
        )

        # 5. Stato del Bot
        embed.add_field(
            name="🤖 Sistema Bot",
            value=f"• Ping: **{round(self.bot.latency * 1000)}ms**\n• Host: **Render (24/7)**",
            inline=True
        )

        # Riga dei comandi rapidi pulita
        embed.add_field(
            name="📌 Collegamenti Rapidi",
            value="Usa i comandi ` / ` per interagire con i quiz, i ticket e i suggerimenti nel server!",
            inline=False
        )

        embed.set_footer(text=f"ID Server: {guild.id} • Ultimo aggiornamento live")

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