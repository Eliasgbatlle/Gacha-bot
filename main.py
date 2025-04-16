import discord
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'🌐 En {len(bot.guilds)} servidores')
    print("⚡ Comandos slash listos.")

# Carga tus extensiones (cogs)
modules = [
    'modules.economy.bank',
    'modules.economy.work',
    'modules.gacha.rolls',
]

for module in modules:
    try:
        bot.load_extension(module)
        print(f'✅ Módulo {module} cargado con éxito')
    except Exception as e:
        print(f'❌ Error al cargar {module}: {e}')

# Arranca el bot
bot.run(TOKEN)
