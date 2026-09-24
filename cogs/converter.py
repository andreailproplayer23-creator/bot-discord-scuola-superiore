import discord
from discord.ext import commands
import config

class ConverterModal(discord.ui.Modal, title="🧮 Toolbox Convertitore Informatico"):
    input_valore = discord.ui.TextInput(
        label="Valore o Numero da convertire",
        placeholder="Es. 42 oppure 1024",
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )

    tipo_conversione = discord.ui.TextInput(
        label="Tipo (bin, hex, ascii, byte, base64)",
        placeholder="Scrivi: bin, hex, ascii, byte o base64",
        style=discord.TextStyle.short,
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Rsp = None): # type: ignore
        valore_str = self.input_valore.value.strip()
        tipo = self.tipo_conversione.value.strip().lower()
        
        risultato = ""
        try:
            if tipo == "bin":
                num = int(valore_str)
                risultato = f"Binario: `{bin(num)}` | Ottale: `{oct(num)}` | Esadecimale: `{hex(num)}`"
            elif tipo == "hex":
                num = int(valore_str, 16)
                risultato = f"Decimale: `{num}` | Binario: `{bin(num)}`"
            elif tipo == "ascii":
                if len(valore_str) == 1:
                    risultato = f"Codice ASCII (Dec): `{ord(valore_str)}` | Hex: `{hex(ord(valore_str))}`"
                else:
                    chars = [str(ord(c)) for c in valore_str]
                    risultato = f"Codici ASCII: `{' '.join(chars)}`"
            elif tipo == "byte":
                num = float(valore_str)
                kb = num / 1024
                mb = kb / 1024
                gb = mb / 1024
                risultato = f"• Kilobyte (KB): `{kb:.4f}`\n• Megabyte (MB): `{mb:.4f}`\n• Gigabyte (GB): `{gb:.4f}`"
            elif tipo == "base64":
                import base64
                encoded = base64.b64encode(valore_str.encode('utf-8')).decode('utf-8')
                risultato = f"Base64: `{encoded}`"
            else:
                risultato = "❌ Tipo non riconosciuto! Usa: `bin`, `hex`, `ascii`, `byte` o `base64`."

            embed = discord.Embed(
                title="✨ Risultato Conversione",
                description=f"**Input:** `{valore_str}` (Modo: `{tipo}`)\n\n{risultato}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Errore: Assicurati di aver inserito un numero o un valore valido per il tipo selezionato.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Si è verificato un errore: {e}", ephemeral=True)

class ConverterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Avvia Convertitore", style=discord.ButtonStyle.primary, emoji="🔢", custom_id="persistent_converter_btn")
    async def open_converter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConverterModal())

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ConverterView()) # Rende il pulsante persistente

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(config.CHANNEL_CONVERTER)
        if not channel:
            return

        # Pulisce il canale e invia il pannello fisso
        async for message in channel.history(limit=10):
            if message.author == self.bot.user:
                return # Esiste già il pannello

        embed = discord.Embed(
            title="🧮 Toolbox & Convertitore Informatico",
            description="Hai bisogno di convertire un numero in binario, esadecimale, calcolare i byte o codificare in base64 durante lezione o programmazione?\n\nClicca il pulsante qui sotto per aprire il **Modal interattivo**!",
            color=discord.Color.from_rgb(0, 162, 232)
        )
        embed.set_footer(text="1ªB Informatica • Strumenti di Classe")
        
        await channel.send(embed=embed, view=ConverterView())

async def setup(bot):
    await bot.add_cog(ConverterCog(bot))