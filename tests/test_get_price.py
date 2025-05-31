from bot.get_price import fetch_stock_price


def test_api_respuesta_valida_con_precio_y_nombre(monkeypatch):
    # Mock de la respuesta de requests.get
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"close": "152.35", "name": "Apple Inc"}

    monkeypatch.setattr(
        "bot.get_price.requests.get", lambda url, timeout: MockResponse()
    )
    resultado = fetch_stock_price("AAPL", "fake_api_key")
    assert resultado == {"precio": 152.35, "nombre": "Apple Inc", "error": None}


def test_api_sin_precio_devuelve_error(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"name": "Empresa X"}

    monkeypatch.setattr(
        "bot.get_price.requests.get", lambda url, timeout: MockResponse()
    )
    resultado = fetch_stock_price("AAPL", "fake_api_key")
    assert resultado["precio"] is None
    assert resultado["nombre"] is None
    assert resultado["error"] is not None


def test_api_respuesta_con_mensaje_error(monkeypatch):
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"status": "error", "message": "Invalid API key"}

    monkeypatch.setattr(
        "bot.get_price.requests.get", lambda url, timeout: MockResponse()
    )
    resultado = fetch_stock_price("AAPL", "fake_api_key")
    assert resultado["precio"] is None
    assert resultado["nombre"] is None
    assert resultado["error"] is not None


def test_api_lanza_timeout(monkeypatch):
    def mock_get(url, timeout):
        raise TimeoutError("Tiempo de espera agotado")

    monkeypatch.setattr("bot.get_price.requests.get", mock_get)
    resultado = fetch_stock_price("AAPL", "fake_api_key")
    assert resultado["precio"] is None
    assert resultado["nombre"] is None
    assert resultado["error"] is not None
