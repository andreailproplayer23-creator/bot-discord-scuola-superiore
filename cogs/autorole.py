import discord
from discord.ext import commands
import config

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        role_guest = guild.get_role(config.ROLE_GUEST)
        
        if role_guest:
            try:
                await member.add_roles(role_guest, reason="Assegnazione automatica ruolo Ospite all'ingresso.")
            except discord.Forbidden:
                print(f"[ERRORE] Permessi insufficienti per assegnare il ruolo Ospite a {member.name}. Assicurati che il ruolo del bot sia più in alto rispetto al ruolo Ospite.")
            except discord.HTTPException as e:
                print(f"[ERRORE] Errore di connessione o Discord API durante l'assegnazione del ruolo a {member.name}: {e}")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))