import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    """
    Gestor de base de datos SQLite para el seguimiento de precios de activos financieros.
    """

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
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                api_key TEXT
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

    # ================== GESTIÓN DE USUARIOS Y API KEY ==================

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

    def guardar_api_key(self, chat_id: str, api_key: str):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE usuarios SET api_key = ? WHERE chat_id = ?
                """,
                (api_key, chat_id)
            )
            conn.commit()

    def obtener_api_key(self, chat_id: str) -> Optional[str]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT api_key FROM usuarios WHERE chat_id = ?", (chat_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def obtener_usuarios(self) -> List[str]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM usuarios")
            return [row[0] for row in cursor.fetchall()]

    # ================== GESTIÓN DE PRODUCTOS SEGUIDOS ==================

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

    def obtener_productos(
        self, chat_id: str
    ) -> List[Tuple[str, int, str, float, float]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT symbol, intervalo_min, nombre_empresa, limite_inferior, limite_superior
                FROM productos_seguidos
                WHERE chat_id = ?
            """,
                (chat_id,),
            )
            return cursor.fetchall()

    def eliminar_producto(self, chat_id: str, symbol: str):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM productos_seguidos
                WHERE chat_id = ? AND symbol = ?
                """,
                (chat_id, symbol),
            )
            conn.commit()

    def obtener_limites(self, chat_id: str, symbol: str) -> Tuple[float, float]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT limite_inferior, limite_superior
                FROM productos_seguidos
                WHERE chat_id = ? AND symbol = ?
            """,
                (chat_id, symbol),
            )
            return cursor.fetchone()

    # ================== GESTIÓN DEL HISTORIAL DE PRECIOS ==================

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

    def obtener_historial(self, chat_id: str, symbol: str) -> List[Tuple[float, str]]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT precio, timestamp FROM historial_precios
                WHERE chat_id = ? AND symbol = ?
                ORDER BY id DESC
                LIMIT 10
            """,
                (chat_id, symbol),
            )
            return cursor.fetchall()

    def borrar_historial(self, chat_id: str, symbol: str):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM historial_precios
                WHERE chat_id = ? AND symbol = ?
                """,
                (chat_id, symbol),
            )
            conn.commit()

    def obtener_estadisticas(
        self, chat_id: str, symbol: str
    ) -> Tuple[float, float, float]:
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MIN(precio), MAX(precio), AVG(precio)
                FROM historial_precios
                WHERE chat_id = ? AND symbol = ?
            """,
                (chat_id, symbol),
            )
            return cursor.fetchone()

    # ========== Exportar historial para CSV ==========
    def obtener_historial_usuario(self, chat_id: str, ticker: str = None) -> list:
        """
        Devuelve todo el historial de precios de un usuario en formato lista de diccionarios.
        Si se indica ticker, filtra solo para ese símbolo.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            if ticker:
                cursor.execute(
                    """
                    SELECT symbol, precio, timestamp
                    FROM historial_precios
                    WHERE chat_id = ? AND symbol = ?
                    ORDER BY timestamp ASC
                    """,
                    (chat_id, ticker)
                )
            else:
                cursor.execute(
                    """
                    SELECT symbol, precio, timestamp
                    FROM historial_precios
                    WHERE chat_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (chat_id,)
                )
            rows = cursor.fetchall()
            historial = [
                {
                    "Símbolo": row[0],
                    "Precio": row[1],
                    "Fecha": row[2]
                }
                for row in rows
            ]
            return historial

    # ========== Exportar favoritas para CSV ==========
    def obtener_favoritas_usuario(self, chat_id: str) -> list:
        """
        Devuelve todas las acciones favoritas (seguidas) por el usuario como lista de diccionarios.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT symbol, nombre_empresa, intervalo_min, limite_inferior, limite_superior
                FROM productos_seguidos
                WHERE chat_id = ?
                ORDER BY symbol ASC
                """,
                (chat_id,)
            )
            rows = cursor.fetchall()
            favoritas = [
                {
                    "Símbolo": row[0],
                    "Nombre": row[1],
                    "Intervalo (min)": row[2],
                    "Límite Inferior": row[3],
                    "Límite Superior": row[4],
                }
                for row in rows
            ]
            return favoritas
