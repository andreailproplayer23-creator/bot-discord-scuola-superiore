import discord
from discord.ext import commands
import config

class WelcomeExit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        
        # Assegna automaticamente il ruolo notifiche
        notif_role = guild.get_role(config.ROLE_NOTIFICATIONS)
        if notif_role:
            try:
                await member.add_roles(notif_role, reason="Assegnazione automatica ruolo notifiche all'ingresso")
            except discord.HTTPException as e:
                print(f"[ERRORE] Impossibile assegnare il ruolo notifiche a {member.name}: {e}")

        welcome_channel = guild.get_channel(config.CHANNEL_WELCOME)
        
        if welcome_channel:
            try:
                embed = discord.Embed(
                    title="👋 Un nuovo utente è entrato!",
                    description=f"Benvenuto nel server della 1ªB Informatica, {member.mention}!\nVai nel canale delle regole per verificare il tuo account.",
                    color=discord.Color.from_rgb(0, 162, 255)
                )
                if member.display_avatar:
                    embed.set_thumbnail(url=member.display_avatar.url)
                
                await welcome_channel.send(embed=embed)
            except discord.HTTPException as e:
                print(f"[ERRORE] Impossibile inviare il messaggio di benvenuto: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        exit_channel = guild.get_channel(config.CHANNEL_EXIT)
        
        if exit_channel:
            try:
                embed = discord.Embed(
                    title="🚪 Qualcuno ha lasciato il server",
                    description=f"**{member.name}** è uscito dal server.",
                    color=discord.Color.red()
                )
                await exit_channel.send(embed=embed)
            except discord.HTTPException as e:
                print(f"[ERRORE] Impossibile inviare il messaggio di uscita: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeExit(bot))