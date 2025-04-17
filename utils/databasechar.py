import sqlite3
import os
import random
from urllib.parse import urlparse
import requests
import time  # Asegúrate de importar el módulo time al principio de tu archivo

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
    print("🔄 Creando base de datos...")  # Log de inicio
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
    print("✅ Base de datos creada con éxito.")  # Log de éxito

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

def obtener_personajes_top(page=1):
    url = f"https://api.jikan.moe/v4/characters?page={page}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"🔍 Respuesta de la API para la página {page}: {data}")
        time.sleep(0.2)  # Pausa de 0.2 segundos entre solicitudes
        return data.get("data", [])
    elif response.status_code == 429:
        print(f"❌ Error 429: Demasiadas solicitudes. Esperando 30 segundos...")
        time.sleep(30)  # Espera 30 segundos si se alcanza el límite por minuto
        return obtener_personajes_top(page)  # Reintenta la misma página
    else:
        print(f"❌ Error en la solicitud a la API para la página {page}: {response.status_code}")
        return []

def generar_personajes_objetivo(objetivo=1000):
    print(f"🔄 Generando {objetivo} personajes...")
    current_page = 1
    generados = 0

    while generados < objetivo and current_page <= 100:  # Limitar a 100 páginas
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

    print(f"✅ {generados} personajes generados con éxito.")  # Log de éxito


def get_available_characters():
    print("🔄 Obteniendo personajes disponibles...")  # Log de inicio
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personajes WHERE disponible = 1")  # Asumimos que la columna 'disponible' marca personajes disponibles
    personajes = cursor.fetchall()
    conn.close()
    print(f"Personajes disponibles: {personajes}")  # Agregar print aquí para ver los resultados
    if not personajes:
        print("❌ No se encontraron personajes disponibles.")  # Log de no personajes
    else:
        print(f"✅ Se encontraron {len(personajes)} personajes.")  # Log de personajes encontrados

    return personajes

def obtener_todos_los_personajes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM personajes")
    personajes = c.fetchall()
    conn.close()
    
    personajes_list = []
    for personaje in personajes:
        personajes_list.append({
            "id": personaje[0],
            "nombre": personaje[1],
            "genero": personaje[2],
            "rareza": personaje[3],
            "precio_base": personaje[4],
            "precio_actual": personaje[5],
            "serie": personaje[6],
            "popularidad": personaje[7],
        })
    return personajes_list
