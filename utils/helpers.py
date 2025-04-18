import os
import sqlite3
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import discord
import asyncio
from pyppeteer import launch
from PIL import ImageFont

DB_PATH = "personajes.db"
FOLDER_CARTAS = "data/cartas"
FOLDER_GALERIAS = "data/galeria"

# Asegura que las carpetas existen
os.makedirs(FOLDER_CARTAS, exist_ok=True)
os.makedirs(FOLDER_GALERIAS, exist_ok=True)



# Ruta a tu plantilla HTML
PLANTILLA_HTML = "utils/plantilla_tarjeta.html"

async def generar_tarjeta_html(personaje):
    id, nombre, genero, imagen_url, serie, rareza, carta = personaje

    # Leer plantilla y reemplazar valores
    with open(PLANTILLA_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("[NOMBRE]", nombre)
    html = html.replace("[GENERO]", genero)
    html = html.replace("[IMAGEN_URL]", imagen_url)
    html = html.replace("[SERIE]", serie)
    html = html.replace("[RAREZA]", rareza.upper())

    # Guardar HTML temporal
    temp_html_path = f"/tmp/tarjeta_{id}.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Lanzar navegador sin cabeza con pyppeteer para renderizar el HTML como imagen
    browser = await launch(args=["--no-sandbox"])
    page = await browser.newPage()
    await page.setViewport({"width": 512, "height": 768})
    await page.goto(f"file://{temp_html_path}")
    await asyncio.sleep(0.5)  # Pequeña pausa para cargar bien el CSS/imágenes

    output_path = f"/tmp/tarjeta_{id}.png"
    await page.screenshot({"path": output_path})
    await browser.close()

    return output_path

async def crear_carta_personaje(nombre):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre, genero, imagen, serie, rareza FROM personajes WHERE LOWER(nombre) = ?", (nombre.lower(),))
    data = c.fetchone()
    conn.close()

    if not data:
        return None

    id, nombre, genero, imagen_url, serie, rareza = data


    # Validar la URL de la imagen
    if not isinstance(imagen_url, str) or not imagen_url.startswith("http"):
        print(f"URL de imagen no válida para {nombre}, usando imagen predeterminada.")
        imagen_url = "ruta/a/imagen/predeterminada.png"


    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(imagen_url) as resp:
                if resp.status != 200:
                    print(f"❌ No se pudo obtener la imagen para {nombre}. Status: {resp.status}")
                    return None
                bg = Image.open(BytesIO(await resp.read())).convert("RGBA")
    except Exception as e:
        print(f"Error al obtener la imagen para {nombre}: {e}")
        return None

    # Redimensionar y superponer la carta (tipo carta de Pokémon)
    bg = bg.resize((500, 700))
    draw = ImageDraw.Draw(bg)
    font = ImageFont.load_default()

    # Texto básico sobre la imagen
    draw.rectangle([0, 650, 500, 700], fill=(0, 0, 0, 200))
    draw.text((10, 655), f"{nombre} ({rareza})", font=font, fill="white")
    draw.text((10, 685), f"{serie} | ${precio_actual} | Pop: {popularidad}", font=font, fill="white")

    filepath = f"{FOLDER_CARTAS}/{nombre.lower().replace(' ', '_')}.png"
    bg.save(filepath)

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


