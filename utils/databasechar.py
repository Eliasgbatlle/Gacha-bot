import sqlite3
import os
import random
from urllib.parse import urlparse
import requests

DB_PATH = "utils/characters.db"

# Precios base según rareza
PRECIOS_BASE = {
    "E": 500,
    "D": 2000,
    "C": 8000,
    "B": 20000,
    "A": 50000,
    "S": 150000,
    "SS": 500000,
    "SSS": 1000000
}

# Rareza con pesos
RAREZAS = [
    ("E", 30),
    ("D", 25),
    ("C", 15),
    ("B", 10),
    ("A", 8),
    ("S", 6),
    ("SS", 4),
    ("SSS", 2)
]

def crear_db():
    if not os.path.exists("utils"):
        os.makedirs("utils")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    genero TEXT,
                    carta TEXT,
                    nsfw BOOLEAN,
                    serie TEXT,
                    rareza TEXT,
                    precio_base INTEGER,
                    precio_actual INTEGER,
                    popularidad INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'disponible'
                )''')
    conn.commit()
    conn.close()

def insertar_personaje(nombre, genero, imagen, serie, rareza):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    precio = PRECIOS_BASE[rareza]
    
    print(f"Verificando si el personaje {nombre} ya existe en la base de datos...")

    c.execute("SELECT * FROM personajes WHERE nombre = ?", (nombre,))
    if c.fetchone():
        print(f"El personaje {nombre} ya existe, no se insertará.")
        conn.close()
        return
    
    print(f"Insertando el personaje {nombre} en la base de datos...")

    c.execute("INSERT INTO personajes (nombre, genero, carta, nsfw, serie, rareza, precio_base, precio_actual) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (nombre, genero, imagen, genero != "masculino", serie, rareza, precio, precio))
    conn.commit()
    conn.close()


def asignar_rareza():
    total = sum(p for _, p in RAREZAS)
    rand = random.randint(1, total)
    acumulado = 0
    for rareza, peso in RAREZAS:
        acumulado += peso
        if rand <= acumulado:
            return rareza
    return "E"

def obtener_imagen_gelbooru(nombre):
    try:
        api_key = "f059a80db96a1032658f911e8dad84ba207abe8210faf272a4f6da2290b3356f"
        url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={nombre.replace(' ', '_')}&api_key={api_key}&limit=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]["file_url"]
    except:
        return None
    return None

def contar_disponibles():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM personajes WHERE estado = 'disponible'")
    count = c.fetchone()[0]
    conn.close()
    return count

def obtener_personajes_top(page):
    url = f"https://api.jikan.moe/v4/top/characters?page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def generar_personajes_objetivo(objetivo=1000):
    current_page = 1
    generados = 0

    while generados < objetivo:
        print(f"🔄 Revisando personajes de la página {current_page}")
        personajes = obtener_personajes_top(current_page)
        if not personajes:  # Si no hay personajes en la página, detener el ciclo
            break
        
        for personaje in personajes:
            if generados >= objetivo:
                break

            nombre = personaje.get("name")
            character_url = personaje.get("url")
            imagen = personaje.get("images", {}).get("jpg", {}).get("image_url")
            anime_appearance = personaje.get("anime", [])
            if not anime_appearance:
                continue

            parsed = urlparse(character_url)
            try:
                char_id = int(parsed.path.strip("/").split("/")[-1])
            except:
                continue

            try:
                char_info_url = f"https://api.jikan.moe/v4/characters/{char_id}"
                char_info_response = requests.get(char_info_url)
                char_info = char_info_response.json().get("data", {})
                genero_api = char_info.get("gender", "Unknown")
            except:
                continue

            if genero_api not in ["Male", "Female", "Unknown"]:
                continue

            genero = "masculino" if genero_api == "Male" else "femenino"
            serie = anime_appearance[0].get("name", "Desconocida")

            if genero_api in ["Female", "Unknown"]:
                nsfw_imagen = obtener_imagen_gelbooru(nombre)
                if not nsfw_imagen:
                    continue
                imagen = nsfw_imagen

            rareza = asignar_rareza()
            
            # Imprime los datos antes de insertarlos para asegurarte de que todo es correcto
            print(f"Insertando personaje: {nombre}, {genero}, {imagen}, {serie}, {rareza}")
            
            insertar_personaje(nombre, genero, imagen, serie, rareza)
            generados += 1
        
        current_page += 1

    print(f"✅ Se generaron {generados} personajes nuevos.")


def get_available_characters():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nombre, rareza, serie, precio_actual, precio_base FROM personajes WHERE estado = 'disponible'")
    rows = c.fetchall()
    conn.close()

    personajes = []
    for row in rows:
        personajes.append({
            "nombre": row[0],
            "rareza": row[1],
            "serie": row[2],
            "precio": row[3],
            "precio_base": row[4]
        })
    
    print(f"Personajes disponibles: {personajes}")  # Agregar print aquí para ver los resultados
    return personajes
