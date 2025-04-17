import discord
from discord.ext import commands
import sqlite3
import os
from utils.helpers import crear_carta_personaje, crear_galeria_personaje, es_admin
from utils.databasechar import get_available_characters


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

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

    @bot.slash_command(name="info", description="/info <nombre> Muestra la carta de un personaje o todas las cartas de los personajes de una serie.")
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

    @bot.slash_command(name="galeria", description="/galeria <nombre> Muestra tiempo restante de protección y costo diario.")
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

    @bot.slash_command(name="setcarta", description="")
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

    @bot.slash_command(name="personajes", description="Ver una lista de los personajes disponibles para reclamar")
    async def personajes(self, ctx):
        await ctx.defer()
        personajes = get_available_characters()

        if not personajes:
            await ctx.respond("No hay personajes disponibles en este momento.")
            return

        # Paginamos de a 10
        per_page = 10
        pages = [
            personajes[i:i + per_page] for i in range(0, len(personajes), per_page)
        ]

        embeds = []
        for i, page in enumerate(pages):
            embed = discord.Embed(
                title=f"📜 Personajes disponibles (Página {i+1}/{len(pages)})",
                color=discord.Color.purple()
            )
            for personaje in page:
                embed.add_field(
                    name=f"{personaje['nombre']} ({personaje['rareza']})",
                    value=f"ID: `{personaje['id']}`\nGénero: **{personaje['genero']}**\nSerie: *{personaje['serie']}*\nPrecio base: **{personaje['precio_base']}**\nPrecio actual: **{personaje['precio_actual']}**\nPopularidad: **{personaje['popularidad']}**",
                    inline=False
                )
            embeds.append(embed)

        current = 0
        message = await ctx.respond(embed=embeds[current])

        # Si solo hay una página, no hay paginación
        if len(embeds) == 1:
            return

        # Reacciones para navegar
        view = PaginatedView(embeds)
        await message.edit_original_response(view=view)

def setup(bot: discord.Bot):
    print("✅ Characters cargado")
    bot.add_cog(Characters(bot))
