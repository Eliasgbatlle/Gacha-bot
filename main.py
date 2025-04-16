import discord
from dotenv import load_dotenv
import os
import json
import asyncio
import time

load_dotenv()

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    print(f'🌐 En {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="Gacha +18"))

@bot.slash_command(name="ping", description="Verifica la latencia del bot")
async def ping(ctx: discord.ApplicationContext):
    start = time.perf_counter()
    message = await ctx.respond("🏓 Calculando latencia...")
    end = time.perf_counter()
    latency = round((end - start) * 1000)
    await message.edit_original_response(content=f"🏓 Pong! Latencia: {latency}ms")

@bot.event
async def on_application_command_error(ctx, error):
    print(f"❌ Error en slash command: {error}")

async def main():
    modules = [
        'modules.economy.bank',
        'modules.economy.work',
        'modules.gacha.rolls',
    ]
    for module in modules:
        try:
            await bot.load_extension(module)
            print(f'✅ Módulo {module} cargado con éxito')
        except Exception as e:
            print(f'❌ Error al cargar {module}: {e}')

    await bot.start(config["token"])

if __name__ == '__main__':
    asyncio.run(main())
