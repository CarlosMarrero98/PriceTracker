import pytest
from bot import alerts

@pytest.fixture(autouse=True)
def limpiar_alertas():
    # Se ejecuta antes de cada test
    alerts.ALERTAS.clear()

def test_registrar_alerta():
    user_id = 123
    ticker = "AAPL"
    intervalo = 60
    min_price = 150
    max_price = 200

    alerts.registrar_alerta(user_id, ticker, intervalo, min_price, max_price)

    clave = (user_id, ticker.upper())
    assert clave in alerts.ALERTAS
    config = alerts.ALERTAS[clave]

    assert config["intervalo"] == intervalo
    assert config["min"] == min_price
    assert config["max"] == max_price
