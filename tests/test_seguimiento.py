import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bot import seguimiento


@pytest.mark.asyncio
async def test_procesar_usuario_envia_alerta(monkeypatch):
    seguimiento.ultima_revision.clear()
    monkeypatch.setattr("bot.seguimiento.db.obtener_api_key", lambda cid: "API_KEY")
    monkeypatch.setattr(
        "bot.seguimiento.db.obtener_productos",
        lambda cid: [("AAPL", 0, "Apple", 100.0, 200.0)],
    )
    monkeypatch.setattr("bot.seguimiento.db.guardar_precio", lambda cid, sym, p: None)
    monkeypatch.setattr(
        "bot.seguimiento.fetch_stock_price",
        lambda s, k: {"precio": 250.0, "nombre": "Apple", "error": None},
    )

    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    app = MagicMock()
    app.bot = mock_bot

    await seguimiento.procesar_usuario(app, "123")
    mock_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_procesar_usuario_sin_api_key(monkeypatch):
    monkeypatch.setattr("bot.seguimiento.db.obtener_api_key", lambda cid: None)

    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    app = MagicMock()
    app.bot = mock_bot

    await seguimiento.procesar_usuario(app, "123")
    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_procesar_usuario_dentro_de_intervalo(monkeypatch):
    seguimiento.ultima_revision[("123", "AAPL")] = datetime.now()

    monkeypatch.setattr("bot.seguimiento.db.obtener_api_key", lambda cid: "API_KEY")
    monkeypatch.setattr(
        "bot.seguimiento.db.obtener_productos",
        lambda cid: [("AAPL", 1, "Apple", 100.0, 200.0)],
    )

    app = MagicMock()
    app.bot = MagicMock()

    await seguimiento.procesar_usuario(app, "123")
    app.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_procesar_usuario_error_en_api(monkeypatch):
    seguimiento.ultima_revision.clear()
    monkeypatch.setattr("bot.seguimiento.db.obtener_api_key", lambda cid: "API_KEY")
    monkeypatch.setattr(
        "bot.seguimiento.db.obtener_productos",
        lambda cid: [("AAPL", 0, "Apple", 100.0, 200.0)],
    )
    monkeypatch.setattr("bot.seguimiento.db.guardar_precio", lambda cid, sym, p: None)
    monkeypatch.setattr(
        "bot.seguimiento.fetch_stock_price",
        lambda s, k: {"precio": None, "nombre": "Apple", "error": "Error"},
    )

    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    app = MagicMock()
    app.bot = mock_bot

    await seguimiento.procesar_usuario(app, "123")
    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_lanzar_seguimiento_y_comprobar_alertas(monkeypatch):
    monkeypatch.setattr("bot.seguimiento.db.obtener_usuarios", lambda: ["123"])
    monkeypatch.setattr("bot.seguimiento.db.obtener_api_key", lambda cid: None)

    async def fake_sleep(x):
        raise asyncio.CancelledError()

    monkeypatch.setattr("bot.seguimiento.asyncio.sleep", fake_sleep)

    app = MagicMock()
    app.create_task = lambda coro: asyncio.create_task(coro)

    with pytest.raises(asyncio.CancelledError):
        await seguimiento.lanzar_seguimiento(app)
        await asyncio.sleep(0.1)
