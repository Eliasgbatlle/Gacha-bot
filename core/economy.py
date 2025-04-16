import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import random

DATA_PATH = "data/data.json"
COOLDOWN_HORAS = 1

def cargar_datos():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def guardar_datos(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !balance
    @commands.command()
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        data = cargar_datos()
        saldo = data.get(user_id, {}).get("coins", 0)
        await ctx.send(f"💰 {ctx.author.display_name}, tenés {saldo} monedas.")

    # !daily
    @commands.command()
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        data = cargar_datos()
        now = datetime.utcnow().date()

        if user_id not in data:
            data[user_id] = {"coins": 0, "reputation": 0, "last_daily": None, "last_job": None}

        last_daily = data[user_id].get("last_daily")
        if last_daily == str(now):
            await ctx.send("⏳ Ya reclamaste tu recompensa diaria hoy.")
            return

        recompensa = 500
        rep = data[user_id].get("reputation", 0)
        if rep >= 10:
            recompensa += 150  # bonus por buena reputación

        data[user_id]["coins"] += recompensa
        data[user_id]["last_daily"] = str(now)
        guardar_datos(data)

        await ctx.send(f"🎁 {ctx.author.display_name}, recibiste {recompensa} monedas por tu daily.")

    # !work
    @commands.command(aliases=["w"])
    async def work(self, ctx):
        await self.ejecutar_trabajo(ctx, tipo="legal")

    # !crime
    @commands.command()
    async def crime(self, ctx):
        await self.ejecutar_trabajo(ctx, tipo="ilegal")

    async def ejecutar_trabajo(self, ctx, tipo="legal"):
        user_id = str(ctx.author.id)
        data = cargar_datos()
        now = datetime.utcnow()

        if user_id not in data:
            data[user_id] = {"coins": 0, "reputation": 0, "last_daily": None, "last_job": None}

        last_job_str = data[user_id].get("last_job")
        if last_job_str:
            last_job = datetime.fromisoformat(last_job_str)
            if now - last_job < timedelta(hours=COOLDOWN_HORAS):
                restante = timedelta(hours=COOLDOWN_HORAS) - (now - last_job)
                minutos = int(restante.total_seconds() // 60)
                await ctx.send(f"⏳ Esperá {minutos} minutos antes de volver a trabajar o delinquir.")
                return

        if tipo == "legal":
            base_pago = random.randint(150, 250)
            rep_bonus = max(0, data[user_id]["reputation"] // 5) * 10
            total = base_pago + rep_bonus
            frases = [
                f"Limpiaste todo el cum de los integrantes del grupo y ganaste {total} monedas.",
                f"Trabajaste como maid para un otaku virgen. Cobraste {total} monedas y una bofetada.",
                f"Moderaste un server +18 lleno de furries. Te pagaron {total} monedas y traumas.",
            ]
            data[user_id]["reputation"] += 2

        else:  # tipo == "ilegal"
            total = random.randint(300, 450)
            frases = [
                f"Hiciste una estafa con NFTs de waifus robadas y ganaste {total} monedas.",
                f"Secuestraste un bot rival y lo vendiste por {total} monedas.",
                f"Robaste monedas del banco de tu facción y escapaste con {total}.",
            ]
            data[user_id]["reputation"] -= 5

        data[user_id]["coins"] += total
        data[user_id]["last_job"] = now.isoformat()
        guardar_datos(data)

        frase = random.choice(frases)
        await ctx.send(f"💼 {ctx.author.display_name}: {frase}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
