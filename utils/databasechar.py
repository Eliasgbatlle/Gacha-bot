import requests
import sqlite3
import random
import time
import spacy

DB_PATH = "personajes.db"

# Cargar el modelo de spaCy
nlp = spacy.load("en_core_web_sm")

# Total de personajes en la base de datos
TOTAL_PERSONAJES = 1225

def crear_tabla_top():
    """Crea la tabla 'Top' en la base de datos para gestionar el ranking de los personajes."""
    conn = sqlite3.connect("personajes.db")
    cursor = conn.cursor()

    # Crear la tabla 'Top' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Top (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personaje_id INTEGER UNIQUE,  -- ID del personaje en la tabla 'personajes'
            votos INTEGER DEFAULT 0,     -- Cantidad de votos para el personaje
            puesto INTEGER,              -- Puesto actual en el ranking
            propietario_id INTEGER,      -- ID del propietario del personaje
            FOREIGN KEY(personaje_id) REFERENCES personajes(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabla 'Top' creada o ya existía.")

def inicializar_ranking():
    """Inicializa el ranking de los personajes en la tabla 'Top'."""
    conn = sqlite3.connect("personajes.db")
    cursor = conn.cursor()

    # Obtener todos los personajes
    cursor.execute("SELECT id FROM personajes ORDER BY id ASC")
    personajes = cursor.fetchall()

    total_personajes = len(personajes)
    for puesto, (personaje_id,) in enumerate(personajes, start=1):
        votos_iniciales = 5 * (total_personajes - puesto + 1)
        cursor.execute('''
            INSERT OR IGNORE INTO Top (personaje_id, votos, puesto)
            VALUES (?, ?, ?)
        ''', (personaje_id, votos_iniciales, puesto))

    conn.commit()
    conn.close()
    print("✅ Ranking inicializado.")

def actualizar_ranking():
    """Actualiza el ranking de los personajes en la tabla 'Top'."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener el ranking actual ordenado por votos
    cursor.execute('''
        SELECT personaje_id, votos, puesto, propietario_id
        FROM Top
        ORDER BY votos DESC, personaje_id ASC
    ''')
    ranking_actual = cursor.fetchall()

    # Actualizar los puestos y otorgar recompensas si un personaje sube de puesto
    for nuevo_puesto, (personaje_id, votos, puesto_anterior, propietario_id) in enumerate(ranking_actual, start=1):
        if nuevo_puesto != puesto_anterior:
            # Actualizar el puesto en la tabla
            cursor.execute("UPDATE Top SET puesto = ? WHERE personaje_id = ?", (nuevo_puesto, personaje_id))

            # Otorgar recompensa al propietario si el personaje sube de puesto
            if nuevo_puesto < puesto_anterior and propietario_id:
                recompensa = 100 * (puesto_anterior - nuevo_puesto)  # Ejemplo: 100 monedas por cada puesto subido
                otorgar_recompensa(propietario_id, recompensa)

    conn.commit()
    conn.close()
    print("✅ Ranking actualizado.")

def otorgar_recompensa(usuario_id, cantidad):
    """Otorga una recompensa monetaria al usuario."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Actualizar el saldo del usuario
    cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (cantidad, usuario_id))

    conn.commit()
    conn.close()
    print(f"✅ Recompensa de {cantidad} monedas otorgada al usuario {usuario_id}.")

def precio_por_rareza(rareza):
    """Devuelve el precio asociado a cada rareza."""
    precios = {
        "SSS": 1000000,
        "SS": 500000,
        "S": 250000,
        "A": 100000,
        "B": 62500,
        "C": 12500,
        "D": 2500,
        "E": 500,
    }
    return precios.get(rareza, 0)  # Devuelve 0 si la rareza no está definida

def obtener_todos_los_personajes():
    """Obtiene todos los personajes de la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM personajes")
        personajes = cursor.fetchall()
        print(f"🔍 Personajes obtenidos de la base de datos: {len(personajes)}")  # Depuración
        return [
            {
                "id": row[0],
                "nombre": row[1],
                "genero": row[2],
                "imagen": row[3],
                "serie": row[4],
                "rareza": row[5],
                "precio": row[6],
            }
            for row in personajes
        ]
    finally:
        conn.close()

def insertar_personaje(nombre, genero, imagen, serie, rareza, precio):
    """Inserta un personaje en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO personajes (nombre, genero, descripcion, imagen, serie, rareza, precio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, genero, imagen, serie, rareza, precio))
        conn.commit()
        print(f"✅ Personaje insertado: {nombre}")
    except sqlite3.IntegrityError:
        print(f"⚠️ El personaje '{nombre}' ya existe en la base de datos.")
    finally:
        conn.close()

def obtener_genero_desde_anilist(nombre):
    """Obtiene el género de un personaje desde AniList usando su API GraphQL."""
    url = "https://graphql.anilist.co"
    query = """
    query ($search: String) {
        Character(search: $search) {
            gender
        }
    }
    """
    variables = {"search": nombre}

    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        if response.status_code == 200:
            data = response.json()
            genero = data.get("data", {}).get("Character", {}).get("gender", None)
            if genero:
                return genero.lower()  # Convertir a minúsculas para consistencia
        return "desconocido"  # Si no se encuentra el género
    except Exception as e:
        print(f"❌ Error al obtener género desde AniList: {e}")
        return "desconocido"

def asignar_rareza_sexista(personajes):
    """Asigna rarezas a los personajes basándose en porcentajes predefinidos."""
    rarezas = [
        ("SSS", 0.01),  # 1% de los personajes serán SSS
        ("SS", 0.02),   # 2% de los personajes serán SS
        ("S", 0.02),    # 2% de los personajes serán S
        ("A", 0.05),    # 5% de los personajes serán A
        ("B", 0.10),    # 10% de los personajes serán B
        ("C", 0.20),    # 20% de los personajes serán C
        ("D", 0.30),    # 30% de los personajes serán D
        ("E", 0.30)     # 30% de los personajes serán E
    ]

    total_personajes = len(personajes)
    rareza_cantidades = {}
    total_asignado = 0

    # Calcular la cantidad de personajes por rareza
    for rareza, porcentaje in rarezas:
        cantidad = int(total_personajes * porcentaje)
        rareza_cantidades[rareza] = cantidad
        total_asignado += cantidad

    # Ajustar la diferencia si la suma no es exactamente igual al total de personajes
    diferencia = total_personajes - total_asignado
    if diferencia > 0:
        rareza_cantidades["E"] += diferencia  # Ajustar en la rareza más común (E)
    elif diferencia < 0:
        rareza_cantidades["E"] += diferencia  # Reducir en la rareza más común (E)

    # Asignar un identificador único si falta
    for idx, personaje in enumerate(personajes):
        if "id" not in personaje:
            personaje["id"] = idx + 1  # Asignar un ID basado en la posición

    # Asignar rarezas a los personajes según su posición
    personajes_ordenados = sorted(personajes, key=lambda p: p["id"])  # Ordenar por ID
    indice = 0
    for rareza, cantidad in rareza_cantidades.items():
        for _ in range(cantidad):
            if indice < len(personajes_ordenados):
                personajes_ordenados[indice]["rareza"] = rareza
                indice += 1

    # Conteo por rareza para depuración
    conteo_por_rareza = {}
    for personaje in personajes_ordenados:
        rareza = personaje["rareza"]
        conteo_por_rareza[rareza] = conteo_por_rareza.get(rareza, 0) + 1

    print("Conteo por rareza:", conteo_por_rareza)
    return personajes_ordenados

def actualizar_rareza_personajes():
    """Actualiza las rarezas de los personajes en la base de datos según el nuevo límite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener todos los personajes de la base de datos
    cursor.execute("SELECT id, nombre, rareza FROM personajes")
    personajes = [{"id": row[0], "nombre": row[1], "rareza": row[2]} for row in cursor.fetchall()]

    # Asignar nuevas rarezas
    personajes_actualizados = asignar_rareza_sexista(personajes)

    # Actualizar la base de datos con las nuevas rarezas
    for personaje in personajes_actualizados:
        cursor.execute("UPDATE personajes SET rareza = ? WHERE id = ?", (personaje["rareza"], personaje["id"]))

    conn.commit()
    conn.close()
    print("✅ Rarezas actualizadas según el nuevo límite de personajes.")

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

def generar_personajes(cantidad=10, paginas_max=100):
    print(f"🔄 Verificando si ya hay al menos {cantidad} personajes en la base de datos...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personajes")
    total_actual = cursor.fetchone()[0]

    # Cargar todos los nombres existentes en la base de datos
    cursor.execute("SELECT nombre FROM personajes")
    nombres_existentes = {row[0] for row in cursor.fetchall()}  # Usar un conjunto para búsqueda rápida
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

            # Verificar si el personaje ya existe en el conjunto de nombres
            if nombre in nombres_existentes:
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
            nombres_existentes.add(nombre)  # Agregar el personaje al conjunto para evitar duplicados
            time.sleep(0.5)  # Jikan rate limit

        pagina += 1

    personajes_con_rareza = asignar_rareza_sexista(lista_personajes)
    
    for p in personajes_con_rareza:
        precio = precio_por_rareza(p["rareza"])  # Calcula el precio basado en la rareza
        insertar_personaje(p["nombre"], p["genero"], p["imagen"], p["serie"], p["rareza"], precio)
    
    print(f"✅ {len(personajes_con_rareza)} personajes generados con éxito.")