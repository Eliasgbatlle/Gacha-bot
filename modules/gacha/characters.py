import discord
from discord.ext import commands
import sqlite3
from utils.helpers import crear_galeria_personaje
from utils.databasechar import obtener_todos_los_personajes, crear_tabla_top, inicializar_ranking, actualizar_ranking, otorgar_recompensa
from discord.commands import default_permissions
from contextlib import closing
import requests
import random
import unicodedata

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

    def imagen_random_gelbooru(self, personaje_nombre):
        """
        Busca una imagen aleatoria de un personaje en Gelbooru, utilizando su nombre y serie desde la base de datos.
        """
        try:
            # Conexión a la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
    
            # Obtener el personaje y su serie desde la base de datos
            cursor.execute("""
                SELECT nombre, serie
                FROM personajes
                WHERE nombre LIKE ?
            """, (f"%{personaje_nombre}%",))
            personaje = cursor.fetchone()
            conn.close()
    
            if not personaje:
                print(f"❌ No se encontró el personaje '{personaje_nombre}' en la base de datos.")
                return None
    
            nombre, serie = personaje
    
            # Generar variaciones del nombre para la búsqueda
            variaciones = [nombre]
            if " " in nombre:  # Si el nombre tiene un espacio, generar variaciones
                partes = nombre.split(" ")
                if len(partes) == 2:  # Asumimos que tiene nombre y apellido
                    nombre_completo = f"{partes[0]}_{partes[1]}"
                    apellido_primero = f"{partes[1]}_{partes[0]}"
                    variaciones.append(nombre_completo)
                    variaciones.append(apellido_primero)
                    if serie:
                        variaciones.append(f"{nombre_completo} ({serie})")
                        variaciones.append(f"{apellido_primero} ({serie})")
            else:  # Si el nombre no tiene espacios (es una sola palabra)
                if serie:
                    variaciones.append(f"{nombre} ({serie})")
                else:
                    variaciones.append(nombre)  # Agregar el nombre tal cual si no hay serie
    
            # Log de las variaciones generadas
            print(f"🔍 Variaciones generadas para '{personaje_nombre}': {variaciones}")
    
            # Normalizar y buscar cada variación
            for variacion in variaciones:
                # Normalizar el nombre para eliminar caracteres especiales
                nombre_normalizado = unicodedata.normalize('NFKD', variacion).encode('ascii', 'ignore').decode('ascii')
                # Convertir el nombre a minúsculas y reemplazar espacios por guiones bajos
                nombre_tag = nombre_normalizado.lower().replace(" ", "_")
                api_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={nombre_tag}+rating%3Aexplicit&limit=100"
    
                # Log de la URL generada
                print(f"🔗 URL generada: {api_url}")
    
                # Realizar la solicitud
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
    
                    # Verificar si la respuesta contiene imágenes en la clave 'post'
                    if "post" in data and isinstance(data["post"], list):  # La respuesta debe contener una lista en 'post'
                        # Filtrar imágenes válidas
                        imagenes_validas = [
                            item["file_url"]
                            for item in data["post"]
                            if "file_url" in item
                        ]
                        if imagenes_validas:
                            return random.choice(imagenes_validas)  # Devolver una imagen aleatoria
    
        except Exception as e:
            print(f"❌ Error al buscar imágenes en Gelbooru: {e}")
    
        return None

    def votar_personaje(self, personaje_id):
        """Incrementa los votos de un personaje y actualiza el ranking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
    
        # Incrementar los votos del personaje
        cursor.execute("UPDATE Top SET votos = votos + 1 WHERE personaje_id = ?", (personaje_id,))
        conn.commit()
    
        # Actualizar el ranking
        actualizar_ranking()
    
        conn.close()
        print(f"✅ Voto registrado para el personaje con ID {personaje_id}.")

    def buscar_personaje(self, nombre):
        print(f"🔄 Buscando personaje: {nombre}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Especifica EXPLÍCITAMENTE las columnas que necesitas en el orden correcto
        cursor.execute("""
            SELECT id, nombre, genero, imagen, serie, rareza, precio_base, carta
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


    @bot.slash_command(name="imagen", description="Muestra una imagen aleatoria de un personaje desde Gelbooru")
    async def imagen(self, ctx: discord.ApplicationContext, nombre: str):
        """
        Comando para mostrar una imagen aleatoria de un personaje desde Gelbooru.
        """
        try:
            await ctx.defer()
    
            # Reorganizar el nombre en diferentes formatos
            formatos_busqueda = [
                nombre,  # Formato original
                " ".join(nombre.split()[::-1]),  # Revertir el orden (e.g., "Satoru Gojo" -> "Gojo Satoru")
                f"{nombre} (anime)",  # Agregar "(anime)" al final
                f"{' '.join(nombre.split()[::-1])} (anime)"  # Revertir y agregar "(anime)"
            ]
    
            # Intentar buscar imágenes en Gelbooru
            imagen_url = None
            for formato in formatos_busqueda:
                imagen_url = self.imagen_random_gelbooru(formato)
                if imagen_url:
                    break
    
            if not imagen_url:
                return await ctx.followup.send(f"❌ No se encontró ninguna imagen para '{nombre}'.", ephemeral=True)
    
            # Crear el embed con la imagen
            embed = discord.Embed(
                title=f"Imagen de {nombre}",
                description=f"Resultado de búsqueda: `{formato}`",
                color=discord.Color.blurple()
            )
            embed.set_image(url=imagen_url)
    
            await ctx.followup.send(embed=embed)
    
        except Exception as e:
            print(f"Error en comando /imagen: {e}")
            await ctx.respond("❌ Ocurrió un error al buscar la imagen del personaje.", ephemeral=True)
  
    @bot.slash_command(name="info", description="Muestra la información de un personaje")
    async def info(self, ctx: discord.ApplicationContext, nombre: str):
        """
        Comando para mostrar la información de un personaje.
        """
        try:
            await ctx.defer()
    
            # Buscar el personaje por nombre
            personaje = self.buscar_personaje(nombre)
            if not personaje:
                return await ctx.followup.send(f"❌ No se encontró el personaje con el nombre '{nombre}'.", ephemeral=True)
    
            # Crear el embed con la información del personaje
            embed = discord.Embed(
                title=f"Información de {personaje[1]}",
                color=discord.Color.blurple()
            )
            embed.add_field(name="ID", value=f"`{personaje[0]}`", inline=True)
            embed.add_field(name="Rareza", value=f"`{personaje[5].capitalize()}`", inline=True)
            embed.add_field(name="Serie", value=f"`{personaje[4]}`", inline=True)
            embed.add_field(name="Precio Base", value=f"`{personaje[6]}`", inline=True)
            embed.add_field(name="Precio Actual", value=f"`{personaje[7]}`", inline=True)
    
            await ctx.followup.send(embed=embed)
    
        except Exception as e:
            print(f"Error en comando /info: {e}")
            await ctx.respond("❌ Ocurrió un error al mostrar la información del personaje.", ephemeral=True)


    @bot.slash_command(name="top", description="Muestra el ranking de los personajes en el Top")
    async def top(self, ctx: discord.ApplicationContext):
        """
        Comando para mostrar el ranking de los personajes en la tabla 'Top' con paginación.
        """
        try:
            await ctx.defer()
    
            # Conexión a la base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
    
            # Obtener el ranking completo de los personajes
            cursor.execute('''
                SELECT p.id, p.nombre, p.rareza, t.votos, t.puesto
                FROM Top t
                JOIN personajes p ON t.personaje_id = p.id
                ORDER BY t.votos DESC, t.puesto ASC
            ''')
            ranking = cursor.fetchall()
            conn.close()
    
            if not ranking:
                return await ctx.followup.send("No hay personajes en el Top.", ephemeral=True)
    
            # Crear las páginas del ranking
            personajes_por_pagina = 10
            embeds = []
    
            for i in range(0, len(ranking), personajes_por_pagina):
                pagina = ranking[i:i+personajes_por_pagina]
                embed = discord.Embed(
                    title=f"🏆 Ranking de Personajes - Página {i//personajes_por_pagina + 1}/{(len(ranking)-1)//personajes_por_pagina + 1}",
                    color=discord.Color.gold()
                )
                for puesto, (personaje_id, nombre, rareza, votos, _) in enumerate(pagina, start=i+1):
                    embed.add_field(
                        name=f"#{puesto} - {nombre} ({rareza.capitalize()})",
                        value=f"ID: `{personaje_id}`\nVotos: `{votos}`",
                        inline=False
                    )
                embeds.append(embed)
    
            # Enviar el embed inicial con paginación
            view = PaginatedView(embeds)
            await ctx.followup.send(embed=embeds[0], view=view)
    
        except Exception as e:
            print(f"Error en comando /top: {e}")
            await ctx.respond("❌ Ocurrió un error al mostrar el Top.", ephemeral=True)

    @bot.slash_command(name="personajes", description="Ver una lista de los personajes disponibles para reclamar")
    async def personajes(self, ctx):
        """
        Comando para mostrar una lista de personajes disponibles.
        """
        try:
            await ctx.defer()
    
            # 1. Obtener personajes
            personajes = obtener_todos_los_personajes()
            if not personajes:
                return await ctx.followup.send("No hay personajes disponibles.", ephemeral=True)
    
            # 2. Crear las páginas (embeds)
            personajes_por_pagina = 10
            embeds = []
    
            for i in range(0, len(personajes), personajes_por_pagina):
                pagina = personajes[i:i+personajes_por_pagina]
                embed = discord.Embed(
                    title=f"Lista de personajes (pág. {i//personajes_por_pagina + 1}/{(len(personajes)-1)//personajes_por_pagina + 1})",
                    color=discord.Color.blurple()
                )
    
                for p in pagina:
                    embed_value = f"• ID: `{p['id']}`\n• Rareza: {p['rareza'].capitalize()}\n• Serie: {p['serie']}"
                    embed.add_field(
                        name=p['nombre'],
                        value=embed_value,
                        inline=False
                    )
    
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
