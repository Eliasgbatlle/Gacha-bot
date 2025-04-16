import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import asyncio  # Para poder usar async main

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'En {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="Gacha +18"))

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! Latencia: {round(bot.latency * 1000)}ms')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Comando no encontrado. Comandos disponibles: {', '.join([cmd.name for cmd in bot.commands])}")
    else:
        print(f"Error no manejado: {error}")

# ✅ Nueva función async que carga los módulos correctamente
async def main():
    modules = [
        'modules.economy.bank',
        'modules.economy.work',
        'modules.gacha.rolls',
    ]
    for module in modules:
        try:
            await bot.load_extension(module)
            print(f'Módulo {module} cargado con éxito')
        except Exception as e:
            print(f'Error al cargar {module}: {e}')

    await bot.start(config["token"])

# ✅ Inicia el bot usando asyncio
if __name__ == '__main__':
    asyncio.run(main())
