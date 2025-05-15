import pytest
from bot import seguimiento

@pytest.fixture(autouse=True)
def limpiar_seguidas():
    seguimiento.SEGUIDAS.clear()

def test_seguir_accion():
    user_id = 1
    ticker = "aapl"
    seguimiento.seguir_accion(user_id, ticker)
    assert seguimiento.obtener_favoritas(user_id) == ["AAPL"]

def test_dejar_de_seguir():
    user_id = 1
    seguimiento.seguir_accion(user_id, "TSLA")
    seguimiento.dejar_de_seguir(user_id, "TSLA")
    assert seguimiento.obtener_favoritas(user_id) == []

def test_seguir_multiples():
    user_id = 2
    seguimiento.seguir_accion(user_id, "AAPL")
    seguimiento.seguir_accion(user_id, "TSLA")
    favoritas = seguimiento.obtener_favoritas(user_id)
    assert set(favoritas) == {"AAPL", "TSLA"}
