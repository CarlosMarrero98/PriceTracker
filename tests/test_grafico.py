import matplotlib
matplotlib.use('Agg')  # Evita errores en sistemas sin GUI (como servidores CI)

import io
from bot.grafico import generar_grafico

def test_generar_grafico_con_datos(monkeypatch):
    # Simula historial de precios
    monkeypatch.setattr("bot.grafico.obtener_historial", lambda ticker: [150, 155, 160, 158])

    resultado = generar_grafico("AAPL")
    assert isinstance(resultado, io.BytesIO)
    assert resultado.getbuffer().nbytes > 0  # Asegura que tiene contenido

def test_generar_grafico_sin_datos(monkeypatch):
    monkeypatch.setattr("bot.grafico.obtener_historial", lambda ticker: [])

    resultado = generar_grafico("AAPL")
    assert resultado is None
