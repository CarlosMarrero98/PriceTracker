import pytest
from bot import historial

@pytest.fixture(autouse=True)
def limpiar_historial():
    historial.HISTORIAL.clear()

def test_guardar_precio_y_obtener_historial():
    ticker = "AAPL"
    precios = [150, 152, 153, 154]

    for precio in precios:
        historial.guardar_precio(ticker, precio)

    resultado = historial.obtener_historial(ticker)

    assert resultado == precios

def test_historial_limite_maxlen():
    ticker = "TSLA"
    # Añadir 12 valores a una cola de máximo 10
    for i in range(12):
        historial.guardar_precio(ticker, i)

    resultado = historial.obtener_historial(ticker)
    assert len(resultado) == 10
    assert resultado == list(range(2, 12))  # Los dos primeros se descartan
