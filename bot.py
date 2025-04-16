import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Módulos personalizados
from modules.economy import get_balance, daily_reward, work, crime

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Crear instancia del bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# Comandos económicos
@bot.command(name="balance")
async def balance(ctx):
    await get_balance(ctx)

@bot.command(name="daily")
async def daily(ctx):
    await daily_reward(ctx)

@bot.command(name="work")
async def work_command(ctx):
    await work(ctx)

@bot.command(name="crime")
async def crime_command(ctx):
    await crime(ctx)

# Ejecutar bot
bot.run(TOKEN)
