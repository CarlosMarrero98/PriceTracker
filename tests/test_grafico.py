import io

from bot.grafico import generar_grafico


def test_generar_grafico_con_datos(monkeypatch):
    # Simula historial válido
    historial = [
        (150.0, "2024-05-18 10:00:00"),
        (155.0, "2024-05-19 10:00:00"),
        (160.0, "2024-05-20 10:00:00"),
    ]

    class MockDB:
        @staticmethod
        def obtener_historial(chat_id, ticker):
            return historial

    monkeypatch.setattr("bot.grafico.db", MockDB)

    buffer = generar_grafico("123", "AAPL")
    assert isinstance(buffer, io.BytesIO)
    assert buffer.getbuffer().nbytes > 0


def test_generar_grafico_sin_datos(monkeypatch):
    class MockDB:
        @staticmethod
        def obtener_historial(chat_id, ticker):
            return []

    monkeypatch.setattr("bot.grafico.db", MockDB)

    buffer = generar_grafico("123", "AAPL")
    assert buffer is None
