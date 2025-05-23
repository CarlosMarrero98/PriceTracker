import os
import sqlite3
import pytest
import time
from bot.db_manager import DatabaseManager

@pytest.fixture
def db_temp():
    # Crea una única conexión en memoria y la inyecta en todos los métodos del test
    conn = sqlite3.connect(":memory:")
    dbm = DatabaseManager(db_path=":memory:")
    dbm._conectar = lambda: conn  # Monkeypatch para siempre usar la misma conexión
    dbm._crear_tablas()  # Crea las tablas en la conexión
    yield dbm
    conn.close()

def test_tablas_creadas(db_temp):
    tablas_esperadas = {"usuarios", "productos_seguidos", "historial_precios"}

    with db_temp._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas_creadas = {fila[0] for fila in cursor.fetchall()}

    assert tablas_esperadas.issubset(tablas_creadas)

def test_agregar_usuario_inserta_correctamente(db_temp):
    chat_id = "123456"
    username = "usuario_test"

    db_temp.agregar_usuario(chat_id, username)

    with db_temp._conectar() as conn:
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

    with db_temp._conectar() as conn:
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

    with db_temp._conectar() as conn:
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

    with db_temp._conectar() as conn:
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
        ("AAPL", "Apple Inc.", 15, 100.0, 200.0),
        ("TSLA", "Tesla Inc.", 30, 150.0, 300.0),
        ("GOOG", "Google LLC", 45, 90.0, 250.0),
    ]

    for symbol, nombre, intervalo, limite_inf, limite_sup in productos:
        db_temp.agregar_producto(
            chat_id, symbol, nombre, intervalo, limite_inf, limite_sup
        )

    resultado = db_temp.obtener_productos(chat_id)

    # Convertimos a conjunto para evitar errores por el orden
    resultado_esperado = {
        (symbol, intervalo, nombre, limite_inf, limite_sup)
        for (symbol, nombre, intervalo, limite_inf, limite_sup) in productos
    }

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

    with db_temp._conectar() as conn:
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

    with db_temp._conectar() as conn:
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

def test_obtener_estadisticas_calcula_min_max_avg(db_temp):
    chat_id = "123456"
    symbol = "AAPL"
    precios = [100.0, 105.0, 110.0, 95.0, 120.0]

    for precio in precios:
        db_temp.guardar_precio(chat_id, symbol, precio)

    minimo, maximo, media = db_temp.obtener_estadisticas(chat_id, symbol)

    assert minimo == min(precios)
    assert maximo == max(precios)
    assert round(media, 2) == round(sum(precios) / len(precios), 2)

def test_obtener_estadisticas_sin_datos_retorna_none(db_temp):
    chat_id = "999999"
    symbol = "GOOG"

    resultado = db_temp.obtener_estadisticas(chat_id, symbol)

    assert resultado == (None, None, None)

def test_obtener_limites_devuelve_valores_correctos(db_temp):
    chat_id = "123456"
    symbol = "AAPL"
    limite_inf = 120.0
    limite_sup = 180.0

    db_temp.agregar_producto(chat_id, symbol, "Apple Inc.", 15, limite_inf, limite_sup)

    limites = db_temp.obtener_limites(chat_id, symbol)

    assert limites == (limite_inf, limite_sup)

def test_obtener_limites_retorna_none_si_no_existe(db_temp):
    chat_id = "999999"
    symbol = "TSLA"

    limites = db_temp.obtener_limites(chat_id, symbol)

    assert limites is None

def test_eliminar_producto(db_temp):
    chat_id = "123"
    symbol = "AAPL"
    nombre = "Apple Inc."

    # Insertamos un producto
    db_temp.agregar_producto(chat_id, symbol, nombre)

    # Aseguramos que fue insertado
    productos = db_temp.obtener_productos(chat_id)
    assert len(productos) == 1

    # Lo eliminamos
    db_temp.eliminar_producto(chat_id, symbol)

    # Comprobamos que fue eliminado
    productos = db_temp.obtener_productos(chat_id)
    assert productos == []

def test_borrar_historial(db_temp):
    chat_id = "123"
    symbol = "AAPL"

    # Insertamos historial manualmente
    with db_temp._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historial_precios (chat_id, symbol, precio, timestamp) VALUES (?, ?, ?, ?)",
            (chat_id, symbol, 150.0, "2024-05-18 10:00:00"),
        )
        conn.commit()

    # Verificamos que hay historial
    historial = db_temp.obtener_historial(chat_id, symbol)
    assert len(historial) == 1

    # Eliminamos
    db_temp.borrar_historial(chat_id, symbol)

    # Comprobamos que fue eliminado
    historial = db_temp.obtener_historial(chat_id, symbol)
    assert historial == []

def test_obtener_usuarios(db_temp):
    # No debe haber usuarios al principio
    assert db_temp.obtener_usuarios() == []

    # Insertamos dos usuarios
    db_temp.agregar_usuario("111", "usuario1")
    db_temp.agregar_usuario("222", "usuario2")

    usuarios = db_temp.obtener_usuarios()

    assert isinstance(usuarios, list)
    assert "111" in usuarios
    assert "222" in usuarios
    assert len(usuarios) == 2

def test_obtener_favoritas_usuario_devuelve_lista_correcta(db_temp):
    chat_id = "123456"
    productos = [
        ("AAPL", "Apple Inc.", 15, 100.0, 200.0),
        ("TSLA", "Tesla Inc.", 30, 150.0, 300.0),
    ]

    for symbol, nombre, intervalo, limite_inf, limite_sup in productos:
        db_temp.agregar_producto(
            chat_id, symbol, nombre, intervalo, limite_inf, limite_sup
        )

    favoritas = db_temp.obtener_favoritas_usuario(chat_id)

    # Debe ser una lista de diccionarios con las claves correctas
    assert isinstance(favoritas, list)
    assert all(isinstance(item, dict) for item in favoritas)
    assert set(favoritas[0].keys()) == {
        "Símbolo", "Nombre", "Intervalo (min)", "Límite Inferior", "Límite Superior"
    }

    # Comprobamos que los valores coinciden con los insertados
    symbols_insertados = {p[0] for p in productos}
    symbols_favoritas = {item["Símbolo"] for item in favoritas}
    assert symbols_insertados == symbols_favoritas

def test_obtener_favoritas_usuario_vacia_si_no_hay_productos(db_temp):
    chat_id = "999999"
    favoritas = db_temp.obtener_favoritas_usuario(chat_id)
    assert favoritas == []
