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

async def crear_carta_personaje(personaje):
    # Desempaquetamos la tupla
    id, nombre, genero, imagen_url, serie, rareza, carta = personaje

    print(f"🖼️ Descargando imagen del personaje: {nombre}")
    async with aiohttp.ClientSession() as session:
        async with session.get(imagen_url) as resp:
            if resp.status != 200:
                raise Exception("No se pudo descargar la imagen del personaje.")
            img_bytes = await resp.read()

    # Crear imagen base
    img = Image.new("RGBA", (512, 768), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Cargar imagen del personaje
    personaje_img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    personaje_img = personaje_img.resize((512, 512))
    img.paste(personaje_img, (0, 0))

    # Texto
    fuente_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Cambia si querés una fuente anime
    font = ImageFont.truetype(fuente_path, 24)

    draw.rectangle([(0, 512), (512, 768)], fill=(0, 0, 0, 180))  # Fondo del texto

    draw.text((10, 520), f"Nombre: {nombre}", fill="white", font=font)
    draw.text((10, 560), f"Rareza: {rareza}", fill="white", font=font)
    draw.text((10, 600), f"Género: {genero}", fill="white", font=font)
    draw.text((10, 640), f"Serie: {serie}", fill="white", font=font)

    # Guardar imagen
    path = f"/tmp/carta_{id}.png"
    img.save(path)
    print(f"✅ Carta creada en: {path}")
    return path

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


