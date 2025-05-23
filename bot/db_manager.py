import sqlite3
from typing import List, Tuple, Optional

class DatabaseManager:
    """
    Gestor de base de datos SQLite para el seguimiento de precios de activos financieros.

    Este gestor se encarga de la creación y mantenimiento de las tablas necesarias
    para registrar usuarios, productos seguidos, historial de precios y configuraciones de alerta.

    Atributos:
        db_path (str): Ruta al archivo de la base de datos SQLite.
    """

    def __init__(self, db_path="basedatos.db"):
        """
        Inicializa el gestor de base de datos y crea las tablas si no existen.

        Args:
            db_path (str, optional): Ruta al archivo de base de datos.
                                     Por defecto es 'basedatos.db'.
        """
        self.db_path = db_path
        self._crear_tablas()

    def _conectar(self):
        """
        Establece una conexión a la base de datos SQLite.

        Returns:
            sqlite3.Connection: Objeto de conexión a la base de datos.
        """
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        """
        Crea las tablas necesarias en la base de datos si aún no existen:

        - usuarios: información básica de los usuarios de Telegram y su API Key de TwelveData.
        - productos_seguidos: activos financieros que sigue cada usuario, con configuración de alertas.
        - historial_precios: registros históricos de precios por símbolo y usuario.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()

            # Tabla de usuarios con API Key
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
        """
        Inserta un nuevo usuario en la base de datos si no existe ya.

        Args:
            chat_id (str): Identificador único del chat de Telegram.
            username (str): Nombre de usuario de Telegram.
        """
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
        """
        Guarda o actualiza la API Key de TwelveData para el usuario.

        Args:
            chat_id (str): Identificador del chat de Telegram.
            api_key (str): Clave de API de TwelveData.
        """
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
        """
        Devuelve la API Key de TwelveData almacenada para el usuario.

        Args:
            chat_id (str): Identificador del chat de Telegram.

        Returns:
            Optional[str]: API Key o None si no está guardada.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT api_key FROM usuarios WHERE chat_id = ?", (chat_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def obtener_usuarios(self) -> List[str]:
        """
        Devuelve una lista con todos los IDs de usuario registrados.

        Returns:
            List[str]: Lista de IDs (chat_id) de todos los usuarios registrados en la base de datos.
        """
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
        """
        Añade o actualiza un activo financiero seguido por un usuario.

        Args:
            chat_id (str): Identificador del chat del usuario.
            symbol (str): Símbolo del activo financiero (ej. 'AAPL').
            nombre_empresa (str): Nombre completo de la empresa o activo.
            intervalo (int, optional): Frecuencia en minutos para revisar el precio. Por defecto 15.
            limite_inf (float, optional): Límite inferior de precio para alertas. Por defecto 0.0.
            limite_sup (float, optional): Límite superior de precio para alertas. Por defecto 0.0.
        """
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
        """
        Recupera la lista de activos financieros seguidos por un usuario.

        Args:
            chat_id (str): Identificador del chat del usuario.

        Returns:
            List[Tuple[str, int, str, float, float]]: Lista de tuplas con la información de los activos.
        """
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
        """
        Elimina un activo financiero que el usuario ha dejado de seguir.

        Args:
            chat_id (str): Identificador del usuario de Telegram.
            symbol (str): Símbolo del activo a eliminar.
        """
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
        """
        Recupera los límites de alerta configurados por el usuario para un activo financiero.

        Args:
            chat_id (str): Identificador del chat del usuario.
            symbol (str): Símbolo del activo financiero.

        Returns:
            Tuple[float, float]: Tupla con (limite_inferior, limite_superior).
        """
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
        """
        Guarda un nuevo registro de precio en el historial para un activo seguido por el usuario.

        Args:
            chat_id (str): Identificador del chat del usuario.
            symbol (str): Símbolo del activo financiero (ej. 'GOOG').
            precio (float): Precio actual del activo.
        """
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
        """
        Obtiene el historial reciente de precios para un activo seguido por un usuario.

        Args:
            chat_id (str): Identificador del chat del usuario.
            symbol (str): Símbolo del activo financiero.

        Returns:
            List[Tuple[float, str]]: Lista de tuplas con el formato (precio, timestamp).
        """
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
        """
        Elimina el historial de precios de un símbolo para un usuario específico.

        Args:
            chat_id (str): ID del usuario de Telegram.
            symbol (str): Símbolo de la acción (ej: "AAPL").
        """
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
        """
        Calcula estadísticas básicas de precios para un activo seguido por un usuario.

        Args:
            chat_id (str): Identificador del chat del usuario.
            symbol (str): Símbolo del activo financiero.

        Returns:
            Tuple[float, float, float]: Tupla con los valores (mínimo, máximo, promedio).
        """
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

    # ========== Exportar historial completo para CSV ==========

    def obtener_historial_usuario(self, chat_id: str) -> list:
        """
        Devuelve todo el historial de precios de un usuario en formato lista de diccionarios.

        Args:
            chat_id (str): Identificador del chat del usuario.

        Returns:
            List[dict]: Lista de registros con las columnas: símbolo, precio, fecha.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
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
            # Convertimos a lista de diccionarios para pandas
            historial = [
                {
                    "Símbolo": row[0],
                    "Precio": row[1],
                    "Fecha": row[2]
                }
                for row in rows
            ]
            return historial
