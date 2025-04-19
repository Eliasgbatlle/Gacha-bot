import discord
from discord.ext import commands
import sqlite3
from utils.helpers import crear_galeria_personaje
from utils.databasechar import obtener_todos_los_personajes
from discord.commands import default_permissions
from contextlib import closing

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class PaginatedView(discord.ui.View):
    def __init__(self, embeds):  # <-- Quita el parámetro timeout aquí
        super().__init__(timeout=60)  # <-- Pon el timeout aquí directamente
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
        print(f"🔄 Buscando personaje: {nombre}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Especifica EXPLÍCITAMENTE las columnas que necesitas en el orden correcto
        cursor.execute("""
            SELECT id, nombre, genero, imagen, serie, rareza, precio_base, precio_actual, popularidad, carta
            FROM personajes 
            WHERE nombre LIKE ?
        """, (f"%{nombre}%",))
        personaje = cursor.fetchone()
        conn.close()

        if personaje:
            print(f"✅ Personaje encontrado: {nombre}")
        else:
            print(f"❌ No se encontró el personaje: {nombre}")

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

    @bot.slash_command(name="personajes", description="Ver una lista de los personajes disponibles para reclamar")
    async def personajes(self, ctx):
        try:
            await ctx.defer()
            
            # 1. Obtener personajes
            personajes = obtener_todos_los_personajes()
            if not personajes:
                return await ctx.followup.send("No hay personajes disponibles.", ephemeral=True)

            # 2. Crear las páginas (embeds)
            personajes_por_pagina = 10
            embeds = []  # <-- Definimos la lista de embeds aquí
            
            for i in range(0, len(personajes), personajes_por_pagina):
                pagina = personajes[i:i+personajes_por_pagina]
                embed = discord.Embed(
                    title=f"Lista de personajes (pág. {i//personajes_por_pagina + 1}/{(len(personajes)-1)//personajes_por_pagina + 1})",  # <-- Cálculo corregido
                    color=discord.Color.blurple()
                )
                
                for p in pagina:
                    embed_value = f"• Rareza: {p['rareza'].capitalize()}\n• Serie: {p['serie']}"
                    embed.add_field(
                        name=p['nombre'],
                        value=embed_value,
                        inline=False
                    )
                
                if len(embed) > 6000:  # Límite de Discord
                    embed.clear_fields()
                    embed.description = "⚠️ Demasiados personajes para mostrar"
                    break
                    
                embeds.append(embed)

            # 3. Enviar con paginación
            view = PaginatedView(embeds)
            await ctx.followup.send(embed=embeds[0], view=view)
            
        except Exception as e:
            print(f"Error en comando /personajes: {e}")
            if not ctx.response.is_done():
                await ctx.respond("❌ Error al procesar el comando", ephemeral=True)
            else:
                await ctx.followup.send("❌ Ocurrió un error al mostrar los personajes", ephemeral=True)


def setup(bot: discord.Bot):
    print("✅ Characters cargado")
    bot.add_cog(Characters(bot))
