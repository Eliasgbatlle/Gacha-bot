import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Cargar módulos
initial_extensions = [
    'core.economy',
    'core.gacha',
    'core.bank',
    'core.reputation',
    'core.theft',
    'core.factions',
    'core.server_scope',
]

for extension in initial_extensions:
    try:
        bot.load_extension(extension)
        print(f"🧩 Módulo cargado: {extension}")
    except Exception as e:
        print(f"❌ Error cargando {extension}: {e}")

bot.run(os.getenv("TOKEN"))

