import requests
import sqlite3
import random
import time

DB_PATH = "personajes.db"

def precio_por_rareza(rareza):
    precios = {
        "SSS": 1000000,
        "SS": 500000,
        "S": 250000,
        "A": 125000,
        "B": 45000,
        "C": 15000,
        "D": 2500,
        "E": 500,
    }
    return precios.get(rareza.upper(), 100)  # Precio por defecto si no se encuentra


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
            precio INTEGER,
            UNIQUE(nombre, serie)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de datos creada con éxito.")

def asignar_rareza_sexista(personajes, total=1000):
    rarezas = [
        ("SSS", 0.01),
        ("SS", 0.02),
        ("S", 0.02),
        ("A", 0.02),
        ("B", 0.05),
        ("C", 0.06),
        ("D", 0.06),
        ("E", 1.00)  # Todo lo que queda
    ]

    # Separar por género
    mujeres = [p for p in personajes if p["genero"].lower() in ["female", "mujer", "femenino"]]
    hombres = [p for p in personajes if p["genero"].lower() in ["male", "hombre", "masculino"]]
    otros = [p for p in personajes if p["genero"].lower() not in ["female", "mujer", "femenino", "male", "hombre", "masculino"]]

    resultado = []

    pos = 0
    for nombre_rareza, proporcion in rarezas:
        cantidad_en_rango = int(proporcion * total)
        mujeres_necesarias = int(cantidad_en_rango * 0.6)
        hombres_necesarios = cantidad_en_rango - mujeres_necesarias

        # Tomar de cada lista si hay disponibles
        for _ in range(mujeres_necesarias):
            if mujeres:
                p = mujeres.pop(0)
                p["rareza"] = nombre_rareza
                resultado.append(p)

        for _ in range(hombres_necesarios):
            if hombres:
                p = hombres.pop(0)
                p["rareza"] = nombre_rareza
                resultado.append(p)

    # Lo que queda, va con rareza E o lo que sobre
    for p in mujeres + hombres + otros:
        p["rareza"] = "E"
        resultado.append(p)

    return resultado


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

# ... [todo tu código sin cambios hasta aquí]

# NUEVA FUNCIÓN para evitar repetidos con delay innecesario
def personaje_existe(nombre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM personajes WHERE nombre = ?", (nombre,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

# Obtener personajes de Jikan API y guardarlos
def generar_personajes(cantidad=10, paginas_max=100):
    print(f"🔄 Verificando si ya hay al menos {cantidad} personajes en la base de datos...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personajes")
    total_actual = cursor.fetchone()[0]
    conn.close()

    if total_actual >= cantidad:
        print(f"✅ Ya hay {total_actual} personajes en la base de datos. No se necesita generar más.")
        return

    print(f"🔄 Generando {cantidad - total_actual} personajes adicionales (máximo {paginas_max} páginas)...")
    personajes_generados = 0
    pagina = 1
    lista_personajes = []

    while personajes_generados < (cantidad - total_actual) and pagina <= paginas_max:
        print(f"📄 Página {pagina}")
        url = f"https://api.jikan.moe/v4/top/characters?page={pagina}&limit=25"
        reintentos = 16
        while reintentos > 0:
            response = requests.get(url)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                print(f"⏳ Rate limit alcanzado (429). Esperando 20 segundos antes de reintentar...")
                time.sleep(20)
                reintentos -= 1
            else:
                print(f"❌ Error al obtener personajes: {response.status_code}")
                return  # Salir por error no manejado

        if response.status_code != 200:
            print(f"❌ No se pudo obtener personajes tras varios intentos.")
            return

        datos = response.json()
        personajes = datos.get("data", [])
        print(f"🔍 Página {pagina} - personajes obtenidos: {len(personajes)}")

        for personaje in personajes:
            if personajes_generados >= (cantidad - total_actual):
                break

            nombre = personaje["name"]

            # Verificar si ya existe antes de hacer llamadas caras
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT 1 FROM personajes WHERE nombre = ?", (nombre,))
            existe = c.fetchone()
            conn.close()

            if existe:
                print(f"⏭️ Personaje ya existe: {nombre}, saltando sin hacer llamadas...")
                continue

            imagen = personaje.get("images", {}).get("jpg", {}).get("image_url", "")
            mal_id = personaje["mal_id"]

            detalles = requests.get(f"https://api.jikan.moe/v4/characters/{mal_id}/full").json()
            genero = obtener_genero_desde_anilist(nombre)
            time.sleep(2)  # AniList rate limit

            animes = detalles.get("data", {}).get("anime", [])
            serie = animes[0]["anime"]["title"] if animes else "Desconocida"

            lista_personajes.append({
                "nombre": nombre,
                "genero": genero,
                "imagen": imagen,
                "serie": serie
            })
            personajes_generados += 1
            time.sleep(0.5)  # Jikan rate limit

        pagina += 1

    personajes_con_rareza = asignar_rareza_sexista(lista_personajes, total=len(lista_personajes))

    for p in personajes_con_rareza:
        insertar_personaje(p["nombre"], p["genero"], p["imagen"], p["serie"], p["rareza"])

    print(f"✅ {len(personajes_con_rareza)} personajes generados con éxito.")

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

import requests

def obtener_genero_desde_anilist(nombre_personaje):
    url_busqueda = "https://graphql.anilist.co"
    
    query = """
    query ($nombre: String) {
      Character (search: $nombre) {
        name {
          full
        }
        gender
      }
    }
    """
    variables = {
        "nombre": nombre_personaje
    }

    response = requests.post(url_busqueda, json={"query": query, "variables": variables})

    if response.status_code == 200:
        datos = response.json()
        if datos.get("data") and datos["data"].get("Character"):
            # Extraer el género
            genero = datos["data"]["Character"].get("gender", "Desconocido")
            return genero.lower() if genero else "desconocido"
    return "desconocido"
