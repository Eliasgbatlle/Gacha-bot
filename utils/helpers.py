import os
import sqlite3
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import discord

DB_PATH = "database.db"
FOLDER_CARTAS = "data/cartas"
FOLDER_GALERIAS = "data/galeria"

# Asegura que las carpetas existen
os.makedirs(FOLDER_CARTAS, exist_ok=True)
os.makedirs(FOLDER_GALERIAS, exist_ok=True)

async def crear_carta_personaje(nombre):
    print(f"🔄 Creando carta para el personaje: {nombre}")  # Log de creación de carta
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nombre, genero, carta, rareza, precio_base, precio_actual, serie, popularidad FROM personajes WHERE LOWER(nombre) = ?", (nombre.lower(),))
    data = c.fetchone()
    conn.close()

    if not data:
        print(f"❌ No se encontró el personaje: {nombre}")  # Log de no encontrado
        return None

    nombre, genero, url_img, rareza, precio_base, precio_actual, serie, popularidad = data

    async with aiohttp.ClientSession() as session:
        async with session.get(url_img) as resp:
            if resp.status != 200:
                print(f"❌ No se pudo descargar la imagen del personaje: {nombre}")  # Log de error de descarga
                return None
            bg = Image.open(BytesIO(await resp.read())).convert("RGBA")

    # Redimensionar y superponer la carta (tipo carta de Pokémon)
    bg = bg.resize((500, 700))
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype("arial.ttf", 30)

    # Texto básico sobre la imagen
    draw.rectangle([0, 650, 500, 700], fill=(0, 0, 0, 200))
    draw.text((10, 655), f"{nombre} ({rareza})", font=font, fill="white")
    draw.text((10, 685), f"{serie} | ${precio_actual} | Pop: {popularidad}", font=font, fill="white")

    filepath = f"{FOLDER_CARTAS}/{nombre.lower().replace(' ', '_')}.png"
    bg.save(filepath)

    print(f"✅ Carta creada y guardada en {filepath}")  # Log de éxito

    return filepath

async def crear_galeria_personaje(nombre):
    print(f"🔄 Creando galería para el personaje: {nombre}")  # Log de creación de galería
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT galeria FROM personajes WHERE LOWER(nombre) = ?", (nombre.lower(),))
    data = c.fetchone()
    conn.close()

    if not data:
        print(f"❌ No se encontró galería para el personaje: {nombre}")  # Log de no encontrado
        return None

    galeria_urls = data[0].split(";") if data[0] else []
    embeds = []

    for url in galeria_urls[:10]:
        embed = discord.Embed(title=f"Galería de {nombre}")
        embed.set_image(url=url)
        embeds.append(embed)

    print(f"✅ Galería creada con {len(embeds)} imágenes.")  # Log de éxito
    return embeds

async def es_admin(ctx):
    return ctx.author.guild_permissions.administrator

async def actualizar_carta(nombre, nueva_url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE personajes SET carta = ? WHERE LOWER(nombre) = ?", (nueva_url, nombre.lower()))
    conn.commit()
    conn.close()

    # Elimina imagen vieja y fuerza regenerar
    filepath = f"{FOLDER_CARTAS}/{nombre.lower().replace(' ', '_')}.png"
    if os.path.exists(filepath):
        os.remove(filepath)

    return await crear_carta_personaje(nombre)


