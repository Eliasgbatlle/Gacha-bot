import discord
from discord.ext import commands
import os
import asyncio
import importlib
from dotenv import load_dotenv

# Cargar variables de entorno (.env o Render)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Intents (asegúrate que estén activados en Discord Dev Portal)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necesario para algunas funciones

# Crear el bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Cargar los módulos (cogs) automáticamente desde la carpeta "modules"
async def cargar_modulos():
    for archivo in os.listdir("./modules"):
        if archivo.endswith(".py"):
            nombre_modulo = archivo[:-3]
            try:
                await bot.load_extension(f"modules.{nombre_modulo}")
                print(f"✅ Módulo cargado: {nombre_modulo}")
            except Exception as e:
                print(f"❌ Error al cargar {nombre_modulo}: {e}")

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    await cargar_modulos()

# Iniciar el bot
if __name__ == "__main__":
    asyncio.run(bot.start(TOKEN))
