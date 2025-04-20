import requests
import sqlite3
import random
import time
import spacy

DB_PATH = "personajes.db"

# Cargar el modelo de spaCy
nlp = spacy.load("en_core_web_sm")

# Total de personajes en la base de datos
TOTAL_PERSONAJES = 1100

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

def analizar_genero_con_spacy(descripcion):
    """Usa spaCy para analizar la descripción y determinar el género."""
    doc = nlp(descripcion.lower())
    palabras_femeninas = {"ella", "chica", "mujer", "princesa", "hermana", "femenina"}
    palabras_masculinas = {"él", "chico", "hombre", "príncipe", "hermano", "masculino"}

    # Buscar palabras clave en el texto
    for token in doc:
        if token.text in palabras_femeninas:
            return "female"
        elif token.text in palabras_masculinas:
            return "male"
    return "unknown"

def actualizar_genero_personajes_desconocidos():
    """Actualiza el género de los personajes con género 'desconocido' usando spaCy."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener personajes con género desconocido
    cursor.execute("SELECT id, nombre, descripcion FROM personajes WHERE genero = 'desconocido'")
    personajes = cursor.fetchall()

    for personaje in personajes:
        personaje_id, nombre, descripcion = personaje
        if not descripcion:  # Si no hay descripción, no se puede analizar
            continue

        # Analizar el género con spaCy
        genero_identificado = analizar_genero_con_spacy(descripcion)
        if genero_identificado != "unknown":
            # Actualizar el género en la base de datos
            cursor.execute("UPDATE personajes SET genero = ? WHERE id = ?", (genero_identificado, personaje_id))
            print(f"🔄 Género actualizado para {nombre}: {genero_identificado}")

    conn.commit()
    conn.close()
    print("✅ Actualización de géneros completada.")

def asignar_rareza_sexista(personajes):
    """Asigna rarezas a los personajes basándose en su posición y el total de personajes."""
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

    # Calcular el número de personajes por rareza
    rareza_cantidades = {}
    for rareza, porcentaje in rarezas:
        rareza_cantidades[rareza] = int(TOTAL_PERSONAJES * porcentaje)

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
            descripcion TEXT,
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

    personajes_con_rareza = asignar_rareza_sexista(lista_personajes)

    for p in personajes_con_rareza:
        insertar_personaje(p["nombre"], p["genero"], p["imagen"], p["serie"], p["rareza"])

    print(f"✅ {len(personajes_con_rareza)} personajes generados con éxito.")