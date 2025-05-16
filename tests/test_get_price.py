import pytest
from bot.get_price import fetch_stock_price

def test_fetch_stock_price_valido(monkeypatch):
    # Mock de la respuesta de requests.get
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "close": "152.35",
                "name": "Apple Inc"
            }

    monkeypatch.setattr("bot.get_price.requests.get", lambda url: MockResponse())

    resultado = fetch_stock_price("AAPL")
    assert resultado == {"price": 152.35, "name": "Apple Inc"}

def test_fetch_stock_price_error(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"status": "error", "message": "Invalid API key"}

    monkeypatch.setattr("bot.get_price.requests.get", lambda url: MockResponse())

    resultado = fetch_stock_price("AAPL")
    assert resultado is None

def test_fetch_stock_price_sin_close(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"name": "Empresa X"}

    monkeypatch.setattr("bot.get_price.requests.get", lambda url: MockResponse())

    resultado = fetch_stock_price("AAPL")
    assert resultado is None
