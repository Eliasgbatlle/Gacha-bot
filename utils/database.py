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
                    protection_until TEXT,  # Fecha en formato ISO (ej: "2025-04-20T12:00:00")
                    is_jailed BOOLEAN DEFAULT FALSE,
                    jail_until TEXT,
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
                    image_url TEXT  # URL de la imagen del personaje
                )
            """)
            conn.commit()

    def get_connection(self):
        """Retorna una conexión a la base de datos."""
        return sqlite3.connect(self.db_path)

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
        return cursor.fetchall()

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

