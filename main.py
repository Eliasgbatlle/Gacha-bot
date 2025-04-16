import discord
from dotenv import load_dotenv
import os
import json
import asyncio

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

# 👇 Cambiamos a discord.Bot para soportar slash commands
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'En {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="Gacha +18"))

# 🆕 Slash command en lugar del viejo @bot.command
@bot.slash_command(name="ping", description="Verifica la latencia del bot")
async def ping(ctx):
    await ctx.respond(f'🏓 Pong! Latencia: {round(bot.latency * 1000)}ms')

# 👇 Manejamos errores solo si mantienes comandos clásicos también
@bot.event
async def on_application_command_error(ctx, error):
    print(f"Error en slash command: {error}")

# Carga dinámica de extensiones (módulos)
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

if __name__ == '__main__':
    asyncio.run(main())
