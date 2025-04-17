import requests
import sqlite3
import random
import time

DB_PATH = "personajes.db"

def crear_base_de_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            genero TEXT,
            imagen TEXT,
            serie TEXT,
            rareza TEXT,
            UNIQUE(nombre, serie)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de datos creada con éxito.")

def asignar_rareza():
    chance = random.random()
    if chance < 0.01:
        return "legendario"
    elif chance < 0.05:
        return "épico"
    elif chance < 0.20:
        return "raro"
    else:
        return "común"

def insertar_personaje(nombre, genero, imagen, serie, rareza):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO personajes (nombre, genero, imagen, serie, rareza)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, genero, imagen, serie, rareza))
        conn.commit()
    except Exception as e:
        print(f"❌ Error al insertar personaje {nombre}: {e}")
    finally:
        conn.close()

def obtener_personajes_top(pagina):
    url = f"https://api.jikan.moe/v4/top/characters?page={pagina}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error al obtener personajes en página {pagina}: {response.status_code}")
        return []
    
    data = response.json()
    personajes = data.get("data", [])
    
    print(f"🔍 Página {pagina} - personajes obtenidos: {len(personajes)}")

    return [
        {
            "mal_id": p.get("mal_id"),
            "url": p.get("url"),
            "name": p.get("name"),
            "image": p.get("images", {}).get("jpg", {}).get("image_url")
        }
        for p in personajes
    ]

def obtener_info_adicional(mal_id):
    url = f"https://api.jikan.moe/v4/characters/{mal_id}/full"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.json().get("data", {})
        genero_api = data.get("gender", "Unknown")
        anime_appearance = data.get("anime", [])
        serie = anime_appearance[0].get("name", "Desconocida") if anime_appearance else "Desconocida"
        return genero_api, serie
    except Exception as e:
        print(f"❌ Error al obtener info adicional de personaje {mal_id}: {e}")
        return None, None

def generar_personajes_objetivo(objetivo=1000):
    print(f"🔄 Generando {objetivo} personajes (máximo 100 páginas)...")
    generados = 0
    current_page = 1
    max_paginas = 100

    while generados < objetivo and current_page <= max_paginas:
        print(f"📄 Página {current_page}")
        personajes = obtener_personajes_top(current_page)
        if not personajes:
            print(f"🔴 No se encontraron personajes en la página {current_page}.")
            break

        for personaje in personajes:
            if generados >= objetivo:
                break

            nombre = personaje.get("name")
            imagen = personaje.get("image")
            mal_id = personaje.get("mal_id")
            if not (nombre and imagen and mal_id):
                continue

            genero_api, serie = obtener_info_adicional(mal_id)
            if genero_api not in ["Male", "Female", "Unknown"]:
                continue

            genero = "masculino" if genero_api == "Male" else "femenino"

            rareza = asignar_rareza()
            print(f"📥 Insertando personaje: {nombre}, {genero}, {serie}, rareza: {rareza}")
            insertar_personaje(nombre, genero, imagen, serie, rareza)
            generados += 1

            time.sleep(0.5)  # Para evitar sobrecargar la API (máx 3 req/seg)

        current_page += 1

    print(f"✅ {generados} personajes generados con éxito.")
