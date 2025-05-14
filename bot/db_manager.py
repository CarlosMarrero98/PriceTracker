import sqlite3
from typing import List, Tuple


class DatabaseManager:
    def __init__(self, db_path="basedatos.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        with self._conectar() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                username TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos_seguidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                nombre_empresa TEXT,
                intervalo_min INTEGER DEFAULT 15,
                limite_inferior REAL,
                limite_superior REAL,
                UNIQUE(chat_id, symbol)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                precio REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()

    def agregar_usuario(self, chat_id: str, username: str):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO usuarios (chat_id, username)
                VALUES (?, ?)
            """,
                (chat_id, username),
            )
            conn.commit()

    def agregar_producto(
        self,
        chat_id: str,
        symbol: str,
        nombre_empresa: str,
        intervalo: int = 15,
        limite_inf: float = 0.0,
        limite_sup: float = 0.0,
    ):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO productos_seguidos (
                    chat_id, symbol, nombre_empresa, intervalo_min, limite_inferior, limite_superior
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (chat_id, symbol, nombre_empresa, intervalo, limite_inf, limite_sup),
            )
            conn.commit()

    
    def obtener_productos(self, chat_id: str) -> List[Tuple[str, int, str]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT symbol, intervalo_min, nombre_empresa
                FROM productos_seguidos
                WHERE chat_id = ?
            """,
                (chat_id,),
            )
            return cursor.fetchall()

    def guardar_precio(self, chat_id: str, symbol: str, precio: float):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO historial_precios (chat_id, symbol, precio)
                VALUES (?, ?, ?)
            """,
                (chat_id, symbol, precio),
            )
            conn.commit()