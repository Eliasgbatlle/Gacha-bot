# Importamos las librerías necesarias
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

load_dotenv()  # Carga las variables del archivo .env
token = os.getenv("DISCORD_TOKEN")

# 1. Configuración inicial del bot
def load_config():
    """Carga la configuración desde config.json (token, prefijo, etc.)"""
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

# 2. Definimos los intents (permisos del bot)
intents = discord.Intents.default()
intents.messages = True  # Necesario para leer mensajes
intents.guilds = True    # Necesario para servidores
intents.message_content = True  # Para leer contenido de mensajes (requerido en v2.0+)

# 3. Creamos la instancia del bot con prefijo y intents
bot = commands.Bot(
    command_prefix=config["prefix"],  # Prefijo de comandos (ej. "!")
    intents=intents,
)

# 4. Evento: Cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'En {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="Gacha +18"))  # Estado del bot

# 5. Cargar módulos dinámicamente
def load_modules():
    """Carga todos los módulos de la carpeta /modules"""
    modules = [
        'modules.economy.bank',
        'modules.gacha.rolls',
        # Añade aquí otros módulos
    ]
    for module in modules:
        try:
            bot.load_extension(module)
            print(f'Módulo {module} cargado con éxito')
        except Exception as e:
            print(f'Error al cargar {module}: {e}')

# 6. Comando básico de prueba
@bot.command(name='ping')
async def ping(ctx):
    """Verifica la latencia del bot"""
    await ctx.send(f'🏓 Pong! Latencia: {round(bot.latency * 1000)}ms')

# 7. Ejecutar el bot
if __name__ == '__main__':
    load_modules()  # Cargamos módulos
    bot.run(config["token"])  # Inicia el bot con el token

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Comando no encontrado. Comandos disponibles: {', '.join([cmd.name for cmd in bot.commands])}")
    else:
        print(f"Error no manejado: {error}")