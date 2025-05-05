import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="gacha_data.db"):
        self.db_path = db_path
        self._initialize_db()  # Crea las tablas si no existen

    def _initialize_db(self):
        """Crea las tablas 'users' y 'characters' si no existen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla 'users' (jugadores)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT NOT NULL,
                    server_id TEXT NOT NULL,
                    coins INTEGER DEFAULT 1000,
                    reputation INTEGER DEFAULT 0,
                    protection_until TEXT,
                    last_daily TEXT,
                    PRIMARY KEY (user_id, server_id)
                )
            """)

            # Tabla 'characters' (personajes gacha)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    character_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    server_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    rarity INTEGER NOT NULL,
                    value INTEGER NOT NULL,
                    stolen BOOLEAN DEFAULT FALSE,
                    protected BOOLEAN DEFAULT TRUE,
                    image_url TEXT  -- URL de la imagen del personaje
                )
            """)

            # Tabla 'servers'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    server_id TEXT PRIMARY KEY,
                    name_id TEXT NOT NULL
                )
            """)

            # Tabla 'global_ranking'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_ranking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    max_score INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def get_connection(self):
        """Retorna una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Esto convierte las filas en diccionarios
        return conn

    # --- Métodos para 'users' ---

    def get_user(self, user_id: str, server_id: str):
        """Obtiene un usuario de la DB (o lo crea si no existe)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE user_id = ? AND server_id = ?",
                (user_id, server_id)
            )
            user = cursor.fetchone()

            if not user:
                # Si no existe, lo crea con valores por defecto
                cursor.execute(
                    "INSERT INTO users (user_id, server_id) VALUES (?, ?)",
                    (user_id, server_id)
                )
                conn.commit()
                return self.get_user(user_id, server_id)  # Retorna el nuevo usuario

            return user

    def can_claim_daily(self, user_id: str, server_id: str) -> (bool, str):
        """Verifica si un usuario puede reclamar la recompensa diaria."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_daily FROM users WHERE user_id = ? AND server_id = ?",
                (user_id, server_id)
            )
            result = cursor.fetchone()

            if not result or not result["last_daily"]:
                return True, ""

            last_daily = datetime.strptime(result["last_daily"], "%Y-%m-%dT%H:%M:%S")
            now = datetime.now()

            if (now - last_daily).total_seconds() >= 24 * 60 * 60:
                return True, ""

            remaining_time = 24 * 60 * 60 - (now - last_daily).total_seconds()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            return False, f"⏳ Ya reclamaste hoy. Vuelve en {hours} horas y {minutes} minutos."

    def update_daily_claim(self, user_id: str, server_id: str):
        """Actualiza la fecha de la última reclamación diaria de un usuario."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_daily = ? WHERE user_id = ? AND server_id = ?",
                (datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), user_id, server_id)
            )
            conn.commit()

    # --- Métodos para 'characters' ---
    def add_character(self, character_data: dict):
        """Añade un personaje a la DB."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO characters (
                    character_id, owner_id, server_id, name, rarity, value, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    character_data["id"],
                    character_data["owner_id"],
                    character_data["server_id"],
                    character_data["name"],
                    character_data["rarity"],
                    character_data["value"],
                    character_data.get("image_url", "")
                )
            )
            conn.commit()

    def get_characters(self, owner_id: str, server_id: str):
        """Obtiene todos los personajes de un usuario."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM characters WHERE owner_id = ? AND server_id = ?",
                (owner_id, server_id)
            )
            return cursor.fetchall()  # Ahora devuelve los resultados como diccionarios

    def update_user(self, user_id: str, server_id: str, data: dict):
        """Actualiza datos de un usuario."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join(f"{key} = ?" for key in data.keys())
            values = list(data.values()) + [user_id, server_id]
            cursor.execute(
                f"UPDATE users SET {set_clause} WHERE user_id = ? AND server_id = ?",
                values
            )
            conn.commit()
