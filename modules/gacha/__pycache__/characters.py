import discord
from discord.ext import commands
import sqlite3
import os
from utils.helpers import crear_carta_personaje, crear_galeria_personaje, es_admin

class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "database.db"

    def buscar_personaje(self, nombre):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personajes WHERE nombre LIKE ?", (f"%{nombre}%",))
        personaje = cursor.fetchone()
        conn.close()
        return personaje

    def buscar_por_serie(self, nombre_serie):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personajes WHERE serie LIKE ?", (f"%{nombre_serie}%",))
        personajes = cursor.fetchall()
        conn.close()
        return personajes

    @commands.command()
    async def info(self, ctx, *, nombre):
        personaje = self.buscar_personaje(nombre)
        if personaje:
            # Mostrar info del personaje con carta
            carta_path = crear_carta_personaje(personaje)
            file = discord.File(carta_path, filename="carta.png")
            await ctx.send(file=file)
        else:
            personajes = self.buscar_por_serie(nombre)
            if personajes:
                await ctx.send(f"Serie encontrada: {nombre}. Enviando cartas de personajes...")
                for personaje in personajes:
                    carta_path = crear_carta_personaje(personaje)
                    file = discord.File(carta_path, filename="carta.png")
                    await ctx.send(file=file)
            else:
                await ctx.send("❌ No se encontró ni personaje ni serie con ese nombre.")

    @commands.command()
    async def galeria(self, ctx, *, nombre):
        personaje = self.buscar_personaje(nombre)
        if personaje:
            imagenes = crear_galeria_personaje(personaje)
            if imagenes:
                for img in imagenes:
                    await ctx.send(img)
            else:
                await ctx.send("❌ No se encontraron imágenes adicionales para este personaje.")
        else:
            await ctx.send("❌ Personaje no encontrado.")

    @commands.command()
    async def setcarta(self, ctx, nombre, url):
        if not es_admin(ctx.author):
            await ctx.send("❌ No tienes permiso para usar este comando.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE personajes SET carta = ? WHERE nombre LIKE ?", (url, f"%{nombre}%"))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ Imagen de carta del personaje `{nombre}` actualizada.")

async def setup(bot):
    await bot.add_cog(Characters(bot))
