import discord
from discord.ext import commands
import os
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Carga o crea archivo data.json
if not os.path.exists("data/data.json"):
    with open("data/data.json", "w") as f:
        json.dump({}, f)

def cargar_datos():
    with open("data/data.json", "r") as f:
        return json.load(f)

def guardar_datos(data):
    with open("data/data.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(os.getenv("TOKEN"))
