import discord
from discord.ext import commands
import sqlite3
import os
from utils.helpers import crear_carta_personaje, crear_galeria_personaje, es_admin
from utils.databasechar import get_available_characters
from utils.databasechar import obtener_todos_los_personajes

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class PaginatedView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.index = 0

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.secondary)
    async def previous(self, button, interaction: discord.Interaction):
        self.index = (self.index - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.secondary)
    async def next(self, button, interaction: discord.Interaction):
        self.index = (self.index + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

class Characters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "personajes.db"

    def buscar_personaje(self, nombre):
        print(f"🔄 Buscando personaje: {nombre}")  # Log de búsqueda
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personajes WHERE nombre LIKE ?", (f"%{nombre}%",))
        personaje = cursor.fetchone()
        conn.close()

        if personaje:
            print(f"✅ Personaje encontrado: {nombre}")  # Log de éxito
        else:
            print(f"❌ No se encontró el personaje: {nombre}")  # Log de no encontrado

        return personaje

    def buscar_por_serie(self, nombre_serie):
        print(f"🔄 Buscando personajes por serie: {nombre_serie}")  # Log de búsqueda por serie
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personajes WHERE serie LIKE ?", (f"%{nombre_serie}%",))
        personajes = cursor.fetchall()
        conn.close()

        if personajes:
            print(f"✅ Se encontraron {len(personajes)} personajes de la serie {nombre_serie}")  # Log de personajes encontrados
        else:
            print(f"❌ No se encontraron personajes de la serie {nombre_serie}")  # Log de no encontrados


        return personajes

    @bot.slash_command(name="info", description="Muestra la carta de un personaje o todas las cartas de los personajes de una serie.")
    async def info(self, ctx, *, nombre):
        personaje = self.buscar_personaje(nombre)
        if personaje:
            # Mostrar info del personaje con carta
            carta_path = await crear_carta_personaje(personaje)
            file = discord.File(carta_path, filename="carta.png")
            await ctx.send(file=file)
        else:
            personajes = self.buscar_por_serie(nombre)
            if personajes:
                await ctx.send(f"Serie encontrada: {nombre}. Enviando cartas de personajes...")
                for personaje in personajes:
                    carta_path = await crear_carta_personaje(personaje)
                    file = discord.File(carta_path, filename="carta.png")
                    await ctx.send(file=file)

            else:
                await ctx.send("❌ No se encontró ni personaje ni serie con ese nombre.")

    @bot.slash_command(name="galeria", description="Muestra tiempo restante de protección y costo diario.")
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
        personajes = obtener_todos_los_personajes()
        if not personajes:
            await ctx.respond("No hay personajes disponibles.")
            return

        personajes_por_pagina = 10
        embeds = []

        for i in range(0, len(personajes), personajes_por_pagina):
            pagina = personajes[i:i+personajes_por_pagina]
            embed = discord.Embed(
                title=f"Lista de personajes (pág. {i//personajes_por_pagina + 1})",
                color=discord.Color.blurple()
            )
            for p in pagina:
                embed.add_field(name=p['nombre'], value=f"{p['rareza'].capitalize()} - {p['serie']}", inline=False)
            embeds.append(embed)

        view = PaginatedView(embeds)
        await ctx.respond(embed=embeds[0], view=view)

def setup(bot: discord.Bot):
    print("✅ Characters cargado")
    bot.add_cog(Characters(bot))
