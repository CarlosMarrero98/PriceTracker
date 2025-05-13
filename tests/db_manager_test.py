import os
import sqlite3
import pytest
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