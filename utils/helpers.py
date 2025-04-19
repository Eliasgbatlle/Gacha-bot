import os
import sqlite3
import discord
import asyncio
from pathlib import Path
from contextlib import closing

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "personajes.db"
FOLDER_CARTAS = BASE_DIR / "data" / "cartas"
FOLDER_GALERIAS = BASE_DIR / "data" / "galeria"
PLANTILLA_HTML = BASE_DIR / "utils" / "card_template.html"

# Crear directorios necesarios
os.makedirs(FOLDER_CARTAS, exist_ok=True)
os.makedirs(FOLDER_GALERIAS, exist_ok=True)

async def crear_galeria_personaje(self, nombre):
    """Versión movida desde helpers.py"""
    with closing(sqlite3.connect(self.db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT galeria FROM personajes WHERE LOWER(nombre) = ?", (nombre.lower(),))
        data = cursor.fetchone()
        
        if not data or not data[0]:
            return None
            
        return [
            discord.Embed(title=f"Galería de {nombre}").set_image(url=url)
            for url in data[0].split(";")[:10]
        ]

async def obtener_datos_personaje(nombre):
    """Obtiene todos los datos de un personaje"""
    with closing(sqlite3.connect(str(DB_PATH))) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, nombre, genero, imagen, serie, rareza, precio_actual, popularidad
            FROM personajes
            WHERE LOWER(nombre) = ?
        """, (nombre.lower(),))
        return c.fetchone()

async def actualizar_carta(nombre, nueva_url):
    """Actualiza la ruta de la carta en la DB"""
    with closing(sqlite3.connect(str(DB_PATH))) as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE personajes SET carta = ?
            WHERE LOWER(nombre) = ?
        """, (nueva_url, nombre.lower()))
        conn.commit()
    
    # Eliminar versión anterior si existe
    old_path = FOLDER_CARTAS / f"{nombre.lower().replace(' ', '_')}.gif"
    if old_path.exists():
        os.remove(old_path)
    
    return nueva_url