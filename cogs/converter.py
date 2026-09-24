import discord
from discord.ext import commands
import config
import base64

class ConverterModal(discord.ui.Modal, title="🧮 Convertitore Informatico"):
    input_valore = discord.ui.TextInput(
        label="Valore o Numero da convertire",
        placeholder="Es. 42, 1024 o una lettera",
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

    async def on_submit(self, interaction: discord.Interaction):
        valore_str = self.input_valore.value.strip()
        tipo = self.tipo_conversione.value.strip().lower()
        
        risultato = ""
        try:
            if tipo == "bin":
                num = int(valore_str)
                risultato = f"• Binario: `{bin(num)}`\n• Ottale: `{oct(num)}`\n• Esadecimale: `{hex(num)}`\n• Decimale: `{num}`"
            elif tipo == "hex":
                num = int(valore_str, 16)
                risultato = f"• Decimale: `{num}`\n• Binario: `{bin(num)}`"
            elif tipo == "ascii":
                if len(valore_str) == 1:
                    risultato = f"• Carattere: `{valore_str}`\n• ASCII (Dec): `{ord(valore_str)}`\n• Hex: `{hex(ord(valore_str))}`"
                else:
                    chars = [str(ord(c)) for c in valore_str]
                    risultato = f"• Codici ASCII: `{' '.join(chars)}`"
            elif tipo == "byte":
                num = float(valore_str)
                kb = num / 1024
                mb = kb / 1024
                gb = mb / 1024
                risultato = f"• Kilobyte (KB): `{kb:.4f}`\n• Megabyte (MB): `{mb:.4f}`\n• Gigabyte (GB): `{gb:.4f}`"
            elif tipo == "base64":
                encoded = base64.b64encode(valore_str.encode('utf-8')).decode('utf-8')
                risultato = f"• Base64 Codificato: `{encoded}`"
            else:
                risultato = "❌ Tipo non riconosciuto! Usa esattamente: `bin`, `hex`, `ascii`, `byte` o `base64`."

            embed = discord.Embed(
                title="✨ Risultato Conversione",
                description=f"**Input inserito:** `{valore_str}` (Modalità: `{tipo}`)\n\n{risultato}",
                color=discord.Color.from_rgb(0, 162, 232)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Errore: Assicurati di aver inserito un numero o un formato valido per il tipo selezionato.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Si è verificato un errore imprevisto: {e}", ephemeral=True)

class ConverterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Avvia Convertitore", style=discord.ButtonStyle.primary, emoji="🔢", custom_id="persistent_converter_btn_1b")
    async def open_converter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConverterModal())

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ConverterView()) # Registra la View in modo permanente

    async def cog_load(self):
        # Si attiva non appena il cog viene caricato
        self.bot.loop.create_task(self.setup_converter_panel())

    async def setup_converter_panel(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(config.CHANNEL_CONVERTER)
        if not channel:
            return

        # Controlla se il pannello esiste già nello storico
        async for message in channel.history(limit=15):
            if message.author == self.bot.user and message.embeds:
                # Trovato! Aggiorna la view per sicurezza
                await message.edit(view=ConverterView())
                return

        # Se non esiste, invia il pannello fisso
        embed = discord.Embed(
            title="🧮 Toolbox & Convertitore Informatico • 1ªB",
            description="Hai bisogno di convertire numeri in binario/esadecimale, calcolare i byte o codificare in base64 durante le lezioni o i progetti?\n\n👉 **Clicca il pulsante qui sotto** per aprire il pannello interattivo!",
            color=discord.Color.from_rgb(0, 162, 232)
        )
        embed.set_footer(text="1ªB Informatica • Strumenti Rapidi")
        
        await channel.send(embed=embed, view=ConverterView())

async def setup(bot):
    await bot.add_cog(ConverterCog(bot))