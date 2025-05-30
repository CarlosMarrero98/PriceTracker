"""
Módulo: db.py

Este módulo implementa el gestor de base de datos SQLite para el proyecto PriceTracker.
Permite gestionar usuarios, API keys, productos seguidos, historial de precios y exportación a CSV.
Compatible con bots de Telegram y preparado para documentación técnica automática.

Autor: Alejandro Pérez Escobar
Fecha: 2024-05-22
"""

import os
import sqlite3
from typing import cast


class DatabaseManager:
    """
    Gestor de base de datos SQLite para el seguimiento de precios de activos financieros.

    Este gestor abstrae todas las operaciones de almacenamiento y recuperación de datos,
    centralizando la lógica de acceso a la base de datos para el bot PriceTracker.
    """

    def __init__(self, db_path: str = "data/basedatos.db") -> None:
        """
        Inicializa el gestor de base de datos, creando las tablas necesarias si no existen.

        Args:
            db_path (str, optional): Ruta del archivo SQLite. Por defecto 'basedatos.db'.
        """
        self.db_path = db_path
        # Solo intentamos crear el directorio si es una ruta real y no una base en memoria
        if db_path != ":memory:":
            dir_name = os.path.dirname(self.db_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

        self._crear_tablas()

    def _conectar(self) -> sqlite3.Connection:
        """
        Abre una nueva conexión a la base de datos SQLite.

        Returns:
            sqlite3.Connection: Objeto de conexión a la base de datos.
        """
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self) -> None:
        """
        Crea las tablas principales (usuarios, productos_seguidos, historial_precios) si no existen.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            # Tabla de usuarios (incluye API Key)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE NOT NULL,
                username TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                api_key TEXT
            );
            """)
            # Tabla de productos seguidos
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
            # Tabla de historial de precios
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

    def agregar_usuario(self, chat_id: str, username: str) -> None:
        """
        Registra un usuario en la base de datos si no existe.

        Args:
            chat_id (str): ID de usuario de Telegram.
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

    def guardar_api_key(self, chat_id: str, api_key: str) -> None:
        """
        Guarda o actualiza la API Key de TwelveData para el usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            api_key (str): Clave API de TwelveData.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE usuarios SET api_key = ? WHERE chat_id = ?
                """,
                (api_key, chat_id),
            )
            conn.commit()

    def obtener_api_key(self, chat_id: str) -> str | None:
        """
        Recupera la API Key de un usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.

        Returns:
            Optional[str]: API Key si existe, None en caso contrario.
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM usuarios WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def obtener_usuarios(self) -> list[str]:
        """
        Devuelve la lista de todos los chat_id de los usuarios registrados.

        Returns:
            List[str]: Lista de chat_id de Telegram.
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
    ) -> None:
        """
        Añade o actualiza un producto seguido por el usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.
            nombre_empresa (str): Nombre de la empresa.
            intervalo (int, optional): Minutos entre comprobaciones. Default 15.
            limite_inf (float, optional): Límite inferior de alerta. Default 0.0.
            limite_sup (float, optional): Límite superior de alerta. Default 0.0.
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

    def obtener_productos(self, chat_id: str) -> list[tuple[str, int, str, float, float]]:
        """
        Obtiene la lista de acciones seguidas por un usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.

        Returns:
            List[Tuple[str, int, str, float, float]]: Lista de tuplas con información de acciones seguidas.
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

    def eliminar_producto(self, chat_id: str, symbol: str) -> None:
        """
        Elimina una acción seguida para un usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.
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

    def obtener_limites(self, chat_id: str, symbol: str) -> tuple[float, float] | None:
        """
        Recupera los límites configurados para una acción seguida por el usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.

        Returns:
            Tuple[float, float]: Límite inferior y superior configurados.
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
            resultado = cursor.fetchone()
            assert resultado is not None, f"No se encontraron límites para {symbol} del usuario {chat_id}"
            return cast(tuple[float, float], resultado)

    # ================== GESTIÓN DEL HISTORIAL DE PRECIOS ==================

    def guardar_precio(self, chat_id: str, symbol: str, precio: float) -> None:
        """
        Guarda un nuevo precio para una acción seguida en el historial del usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.
            precio (float): Precio registrado.
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

    def obtener_historial(self, chat_id: str, symbol: str) -> list[tuple[float, str]]:
        """
        Recupera el historial de precios recientes para una acción de un usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.

        Returns:
            List[Tuple[float, str]]: Lista de tuplas (precio, timestamp), ordenados por fecha descendente.
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

    def borrar_historial(self, chat_id: str, symbol: str) -> None:
        """
        Borra todo el historial de precios para una acción de un usuario.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.
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

    def obtener_estadisticas(self, chat_id: str, symbol: str) -> tuple[float, float, float] | None:
        """
        Calcula estadísticas básicas del historial de precios de una acción.

        Args:
            chat_id (str): ID de usuario de Telegram.
            symbol (str): Ticker de la acción.

        Returns:
            Tuple[float, float, float]: Mínimo, máximo y promedio de precios.
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
            resultado = cursor.fetchone()
            assert resultado is not None, f"No se encontraron precios para {symbol} del usuario {chat_id}"
            return cast(tuple[float, float, float], resultado)

    # ========== Exportar historial para CSV ==========
    def obtener_historial_usuario(self, chat_id: str, ticker: str | None = None) -> list[dict[str, str | float]]:
        """
        Devuelve todo el historial de precios de un usuario en formato lista de diccionarios.

        Si se indica un ticker, filtra solo para ese símbolo.

        Args:
            chat_id (str): ID de usuario de Telegram.
            ticker (str, optional): Ticker de la acción. Si es None, devuelve todo el historial.

        Returns:
            list: Lista de diccionarios con las claves 'Símbolo', 'Precio' y 'Fecha'.
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
                    (chat_id, ticker),
                )
            else:
                cursor.execute(
                    """
                    SELECT symbol, precio, timestamp
                    FROM historial_precios
                    WHERE chat_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (chat_id,),
                )
            rows = cursor.fetchall()
            historial = [{"Símbolo": row[0], "Precio": row[1], "Fecha": row[2]} for row in rows]
            return historial

    # ========== Exportar favoritas para CSV ==========
    def obtener_favoritas_usuario(self, chat_id: str) -> list[dict[str, str | float]]:
        """
        Devuelve todas las acciones favoritas (seguidas) por el usuario como lista de diccionarios.

        Args:
            chat_id (str): ID de usuario de Telegram.

        Returns:
            list: Lista de diccionarios con las claves 'Símbolo', 'Nombre', 'Intervalo (min)', 'Límite
            Inferior' y 'Límite Superior'.
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
                (chat_id,),
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
