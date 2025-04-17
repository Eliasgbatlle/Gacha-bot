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

def asignar_rareza(rank=1, total=1000):
    posicion = rank / total
    if posicion <= 0.01:
        return "SSS"
    elif posicion <= 0.03:
        return "SS"
    elif posicion <= 0.05:
        return "S"
    elif posicion <= 0.07:
        return "A"
    elif posicion <= 0.12:
        return "B"
    elif posicion <= 0.18:
        return "C"
    elif posicion <= 0.24:
        return "D"
    else:
        return "E"

# Insertar personaje solo si no existe
def insertar_personaje(nombre, genero, imagen, serie, rareza):
    conn = sqlite3.connect("personajes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE nombre = ?", (nombre,))
    if c.fetchone():
        print(f"⚠️ Personaje ya existe: {nombre}, saltando...")
        conn.close()
        return

    c.execute("INSERT INTO personajes (nombre, genero, imagen, serie, rareza) VALUES (?, ?, ?, ?, ?)",
              (nombre, genero, imagen, serie, rareza))
    conn.commit()
    conn.close()
    print(f"📥 Insertando personaje: {nombre}, {genero}, {serie}, rareza: {rareza}")

# Obtener personajes de Jikan API y guardarlos
def generar_personajes(cantidad=10, paginas_max=100):
    print(f"🔄 Generando {cantidad} personajes (máximo {paginas_max} páginas)...")
    personajes_generados = 0
    pagina = 1

    while personajes_generados < cantidad and pagina <= paginas_max:
        print(f"📄 Página {pagina}")
        url = f"https://api.jikan.moe/v4/characters?page={pagina}&limit=25"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Error al obtener personajes: {response.status_code}")
            break

        datos = response.json()
        personajes = datos.get("data", [])
        print(f"🔍 Página {pagina} - personajes obtenidos: {len(personajes)}")

        for personaje in personajes:
            if personajes_generados >= cantidad:
                break

            nombre = personaje["name"]
            imagen = personaje.get("images", {}).get("jpg", {}).get("image_url", "")
            mal_id = personaje["mal_id"]

            # Obtener detalles para género y serie
            detalles = requests.get(f"https://api.jikan.moe/v4/characters/{mal_id}/full").json()
            genero = detalles.get("data", {}).get("gender", "Desconocido").lower()
            animes = detalles.get("data", {}).get("anime", [])
            serie = animes[0]["anime"]["title"] if animes else "Desconocida"

            rareza = asignar_rareza(rank=personajes_generados + 1, total=cantidad)

            insertar_personaje(nombre, genero, imagen, serie, rareza)
            personajes_generados += 1

            # Respetar el rate limit de la API
            time.sleep(0.5)

        pagina += 1

    print(f"✅ {personajes_generados} personajes generados con éxito.")

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

def get_available_characters():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, genero, imagen, serie, rareza FROM personajes")
    personajes = cursor.fetchall()
    conn.close()

    # Opcional: convertir a lista de diccionarios si lo prefieres así
    return [
        {
            "nombre": p[0],
            "genero": p[1],
            "imagen": p[2],
            "serie": p[3],
            "rareza": p[4]
        }
        for p in personajes
    ]

# Devolver todos los personajes para usarlos en comandos
def obtener_todos_los_personajes():
    conn = sqlite3.connect("personajes.db")
    c = conn.cursor()
    c.execute("SELECT nombre, genero, imagen, serie, rareza FROM personajes")
    personajes = c.fetchall()
    conn.close()
    return [
        {
            "nombre": p[0],
            "genero": p[1],
            "imagen": p[2],
            "serie": p[3],
            "rareza": p[4]
        }
        for p in personajes
    ]