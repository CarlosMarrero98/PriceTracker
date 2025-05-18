import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.telegram_bot import start, comandos, ayuda, seguir, favoritas, price
from telegram import Update, User, Message


# -------------------------------
# /start
# -------------------------------


@pytest.mark.asyncio
async def test_start_registers_user_and_sends_welcome(monkeypatch):
    mock_update = MagicMock(spec=Update)
    mock_user = MagicMock(spec=User, id=123, username="Saso", first_name="Saso")
    mock_update.effective_user = mock_user

    mock_message = MagicMock(spec=Message)
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_context = MagicMock()

    mock_agregar_usuario = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.agregar_usuario", mock_agregar_usuario)

    await start(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    mock_agregar_usuario.assert_called_once_with("123", "Saso")


# -------------------------------
# /comandos
# -------------------------------


@pytest.mark.asyncio
async def test_comandos_sends_command_list(monkeypatch):
    mock_update = MagicMock(spec=Update)
    mock_message = MagicMock(spec=Message)
    mock_update.message = mock_message
    mock_context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.get_commands_text", lambda: "Comandos")

    await comandos(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Comandos", parse_mode="Markdown"
    )


# -------------------------------
# /ayuda
# -------------------------------


@pytest.mark.asyncio
async def test_ayuda_sends_help_text(monkeypatch):
    mock_update = MagicMock(spec=Update)
    mock_message = MagicMock(spec=Message)
    mock_update.message = mock_message
    mock_context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.get_help_text", lambda: "Ayuda")

    await ayuda(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Ayuda", parse_mode="Markdown"
    )


# -------------------------------
# /seguir
# -------------------------------


@pytest.mark.asyncio
async def test_seguir_sin_args_envia_uso(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = []

    await seguir(update, context)
    update.message.reply_text.assert_called_once_with(
        "Uso: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]"
    )

@pytest.mark.asyncio
async def test_seguir_error_api(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.os.getenv", lambda k: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": None, "nombre": None, "error": "No data"},
    )

    await seguir(update, context)
    update.message.reply_text.assert_called_with("No se pudo seguir 'AAPL': No data")


@pytest.mark.asyncio
async def test_seguir_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.os.getenv", lambda k: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 100.0, "nombre": "Apple", "error": None},
    )
    mock_agregar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.agregar_producto", mock_agregar)

    await seguir(update, context)
    update.message.reply_text.assert_called()
    mock_agregar.assert_called_once()


# -------------------------------
# /favoritas
# -------------------------------


@pytest.mark.asyncio
async def test_favoritas_vacio(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.db.obtener_productos", lambda chat_id: [])

    await favoritas(update, context)
    update.message.reply_text.assert_called_with(
        "Aún no estás siguiendo ninguna acción."
    )


@pytest.mark.asyncio
async def test_favoritas_con_datos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    productos = [("AAPL", 60, "Apple", 100.0, 200.0)]
    monkeypatch.setattr(
        "bot.telegram_bot.db.obtener_productos", lambda chat_id: productos
    )

    await favoritas(update, context)
    update.message.reply_text.assert_called()


# -------------------------------
# /price
# -------------------------------


@pytest.mark.asyncio
async def test_price_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await price(update, context)

    update.message.reply_text.assert_called_once_with("Uso correcto: /price <TICKER>")


@pytest.mark.asyncio
async def test_price_sin_api_key(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.os.getenv", lambda k: None)

    await price(update, context)

    update.message.reply_text.assert_called_once_with(
        "Error: no se ha configurado la clave de la API."
    )


@pytest.mark.asyncio
async def test_price_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.os.getenv", lambda k: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 123.45, "nombre": "Apple Inc.", "error": None},
    )

    await price(update, context)

    update.message.reply_text.assert_called_once_with(
        "📈 *Apple Inc.* (AAPL)\n💰 Precio actual: 123.45$", parse_mode="Markdown"
    )