import os
import sqlite3
import pytest
import time
from bot.db_manager import DatabaseManager


@pytest.fixture
def db_temp():
    # Creamos una base de datos temporal en memoria o archivo
    db_path = "test_temp.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    yield DatabaseManager(db_path=db_path)
    if os.path.exists(db_path):
        os.remove(db_path)


def test_tablas_creadas(db_temp):
    tablas_esperadas = {"usuarios", "productos_seguidos", "historial_precios"}

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas_creadas = {fila[0] for fila in cursor.fetchall()}

    assert tablas_esperadas.issubset(tablas_creadas)


def test_agregar_usuario_inserta_correctamente(db_temp):
    chat_id = "123456"
    username = "usuario_test"

    db_temp.agregar_usuario(chat_id, username)

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT chat_id, username FROM usuarios WHERE chat_id = ?", (chat_id,)
        )
        fila = cursor.fetchone()

    assert fila is not None
    assert fila[0] == chat_id
    assert fila[1] == username


def test_agregar_usuario_no_duplica_si_existe(db_temp):
    chat_id = "123456"
    username = "usuario_test"

    db_temp.agregar_usuario(chat_id, username)
    db_temp.agregar_usuario(chat_id, username)  # Segunda vez

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE chat_id = ?", (chat_id,))
        count = cursor.fetchone()[0]

    assert count == 1


def test_agregar_producto_inserta_correctamente(db_temp):
    chat_id = "123456"
    symbol = "AAPL"
    nombre_empresa = "Apple Inc."
    intervalo = 30
    limite_inf = 100.0
    limite_sup = 200.0

    db_temp.agregar_producto(
        chat_id, symbol, nombre_empresa, intervalo, limite_inf, limite_sup
    )

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT chat_id, symbol, nombre_empresa, intervalo_min, limite_inferior, limite_superior
            FROM productos_seguidos
            WHERE chat_id = ? AND symbol = ?
        """,
            (chat_id, symbol),
        )
        fila = cursor.fetchone()

    assert fila == (chat_id, symbol, nombre_empresa, intervalo, limite_inf, limite_sup)


def test_agregar_producto_reemplaza_si_existe(db_temp):
    chat_id = "123456"
    symbol = "AAPL"

    # Inserción inicial
    db_temp.agregar_producto(chat_id, symbol, "Apple Inc.", 15, 100.0, 200.0)

    # Inserción que debería reemplazar
    db_temp.agregar_producto(
        chat_id, symbol, "Apple Inc. Actualizado", 60, 120.0, 180.0
    )

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nombre_empresa, intervalo_min, limite_inferior, limite_superior
            FROM productos_seguidos
            WHERE chat_id = ? AND symbol = ?
        """,
            (chat_id, symbol),
        )
        fila = cursor.fetchone()

    assert fila == ("Apple Inc. Actualizado", 60, 120.0, 180.0)

def test_obtener_productos_devuelve_lista_correcta(db_temp):
    chat_id = "123456"

    productos = [
        ("AAPL", "Apple Inc.", 15),
        ("TSLA", "Tesla Inc.", 30),
        ("GOOG", "Google LLC", 45),
    ]

    for symbol, nombre, intervalo in productos:
        db_temp.agregar_producto(chat_id, symbol, nombre, intervalo)

    resultado = db_temp.obtener_productos(chat_id)

    # Convertimos a conjunto para que no importe el orden
    resultado_esperado = {(p[0], p[2], p[1]) for p in productos}
    resultado_obtenido = set(resultado)

    assert resultado_obtenido == resultado_esperado


def test_obtener_productos_lista_vacia_si_no_hay_productos(db_temp):
    chat_id = "999999"
    resultado = db_temp.obtener_productos(chat_id)
    assert resultado == []

def test_guardar_precio_inserta_entrada_correcta(db_temp):
    chat_id = "123456"
    symbol = "AAPL"
    precio = 150.25

    db_temp.guardar_precio(chat_id, symbol, precio)

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT chat_id, symbol, precio
            FROM historial_precios
            WHERE chat_id = ? AND symbol = ?
        """,
            (chat_id, symbol),
        )
        fila = cursor.fetchone()

    assert fila is not None
    assert fila[0] == chat_id
    assert fila[1] == symbol
    assert fila[2] == precio


def test_guardar_precio_permite_multiples_registros(db_temp):
    chat_id = "123456"
    symbol = "AAPL"
    precios = [150.25, 151.00, 149.80]

    for precio in precios:
        db_temp.guardar_precio(chat_id, symbol, precio)

    with sqlite3.connect(db_temp.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT precio FROM historial_precios
            WHERE chat_id = ? AND symbol = ?
        """,
            (chat_id, symbol),
        )
        resultados = [fila[0] for fila in cursor.fetchall()]

    assert resultados == precios

def test_obtener_historial_devuelve_los_ultimos_10(db_temp):
    chat_id = "123456"
    symbol = "AAPL"

    # Insertamos 12 precios (solo deben devolver los últimos 10)
    precios = [100 + i for i in range(12)]  # 100, 101, ..., 111

    for precio in precios:
        db_temp.guardar_precio(chat_id, symbol, precio)
        time.sleep(0.01)  # Asegura timestamps distintos

    historial = db_temp.obtener_historial(chat_id, symbol)

    assert len(historial) == 10

    # Extraemos los precios y comprobamos que están en orden descendente
    precios_obtenidos = [fila[0] for fila in historial]
    assert precios_obtenidos == precios[-1:-11:-1]  # últimos 10 en orden inverso


def test_obtener_historial_lista_vacia_si_no_hay_registros(db_temp):
    chat_id = "999999"
    symbol = "MSFT"

    historial = db_temp.obtener_historial(chat_id, symbol)

    assert historial == []