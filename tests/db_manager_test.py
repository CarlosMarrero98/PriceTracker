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
