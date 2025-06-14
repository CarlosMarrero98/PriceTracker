from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import matplotlib
import pytest
from telegram import Message, Update, User

matplotlib.use("Agg")
from bot.telegram_bot import (
    PEDIR_API_KEY,
    ayuda,
    borrar_historial,
    comandos,
    dejar,
    favoritas,
    grafico,
    guardar,
    historial,
    media_historial,
    pedir_api_key,
    price,
    recibir_api_key,
    seguir,
    start,
)

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


@pytest.mark.asyncio
async def test_start_sin_user():
    update = MagicMock(spec=Update)
    update.effective_user = None
    update.message = MagicMock()
    context = MagicMock()

    from bot.telegram_bot import start

    result = await start(update, context)
    assert result is None


@pytest.mark.asyncio
async def test_start_sin_api_key(monkeypatch):
    update = MagicMock(spec=Update)
    user = MagicMock(id=1, username=None, first_name="Carlos")
    update.effective_user = user
    message = MagicMock()
    update.message = message
    context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.db.agregar_usuario", lambda *a: None)
    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda *a: None)
    monkeypatch.setattr("bot.telegram_bot.pedir_api_key", AsyncMock(return_value=PEDIR_API_KEY))

    from bot.telegram_bot import start

    result = await start(update, context)

    assert result == PEDIR_API_KEY


@pytest.mark.asyncio
async def test_start_con_api_key(monkeypatch):
    update = MagicMock(spec=Update)
    user = MagicMock(id=123, username="usuario_test", first_name="Carlos")
    update.effective_user = user

    message = MagicMock()
    message.reply_text = AsyncMock()
    update.message = message

    context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.db.agregar_usuario", lambda chat_id, username: None)
    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "123456")

    from bot.telegram_bot import start

    result = await start(update, context)

    message.reply_text.assert_called_once()
    assert result is None


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
    mock_update.message.reply_text.assert_called_once_with("Comandos", parse_mode="Markdown")


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
    mock_update.message.reply_text.assert_called_once_with("Ayuda", parse_mode="Markdown")


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
    update.message.reply_text.assert_called_once_with("Uso: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]")


@pytest.mark.asyncio
async def test_seguir_error_api(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": None, "nombre": None, "error": "No data"},
    )

    await seguir(update, context)
    update.message.reply_text.assert_called_with("No se pudo seguir 'AAPL': No data")


@pytest.mark.asyncio
async def test_seguir_argumentos_invalidos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL", "60", "limite_mal", "200"]

    await seguir(update, context)
    update.message.reply_text.assert_called_once_with("Intervalo y límites deben ser válidos.")


@pytest.mark.asyncio
async def test_seguir_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 100.0, "nombre": "Apple", "error": None},
    )
    mock_agregar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.agregar_producto", mock_agregar)

    await seguir(update, context)
    update.message.reply_text.assert_called()
    mock_agregar.assert_called_once()


@pytest.mark.asyncio
async def test_seguir_completo(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL", "30", "100", "200"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda *_: "clave")
    monkeypatch.setattr("bot.telegram_bot.fetch_stock_price", lambda *_: {"error": None, "nombre": "Apple"})
    monkeypatch.setattr("bot.telegram_bot.db.agregar_producto", lambda *_: None)

    from bot.telegram_bot import seguir

    await seguir(update, context)
    update.message.reply_text.assert_called_once()


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
    update.message.reply_text.assert_called_with("Aún no estás siguiendo ninguna acción.")


@pytest.mark.asyncio
async def test_favoritas_con_datos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    productos = [("AAPL", 60, "Apple", 100.0, 200.0)]
    monkeypatch.setattr("bot.telegram_bot.db.obtener_productos", lambda chat_id: productos)

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

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: None)

    await price(update, context)

    update.message.reply_text.assert_called_once_with(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )


@pytest.mark.asyncio
async def test_price_con_error(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda *_: "clave")
    monkeypatch.setattr("bot.telegram_bot.fetch_stock_price", lambda *_: {"error": "No válido"})

    from bot.telegram_bot import price

    await price(update, context)
    update.message.reply_text.assert_called_once_with("No se pudo obtener el precio de 'AAPL': No válido")


@pytest.mark.asyncio
async def test_price_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 123.45, "nombre": "Apple Inc.", "error": None},
    )

    await price(update, context)

    update.message.reply_text.assert_called_once_with(
        "📈 *Apple Inc.* (AAPL)\n💰 Precio actual: 123.45$", parse_mode="Markdown"
    )


# -------------------------------
# /historial
# -------------------------------


@pytest.mark.asyncio
async def test_historial_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await historial(update, context)
    update.message.reply_text.assert_called_once_with("Uso correcto: /historial <TICKER>")


@pytest.mark.asyncio
async def test_historial_sin_api_key(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: None)

    await historial(update, context)
    update.message.reply_text.assert_called_once_with(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )


@pytest.mark.asyncio
async def test_historial_ticker_invalido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": None, "nombre": None, "error": "Invalid ticker"},
    )

    await historial(update, context)
    update.message.reply_text.assert_called_once_with("Ticker 'AAPL' no válido o no disponible: Invalid ticker")


@pytest.mark.asyncio
async def test_historial_vacio(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 123.45, "nombre": "Apple Inc.", "error": None},
    )
    monkeypatch.setattr("bot.telegram_bot.db.obtener_historial", lambda chat_id, ticker: [])

    await historial(update, context)
    update.message.reply_text.assert_called_once_with("📭 No hay historial guardado para AAPL.")


@pytest.mark.asyncio
async def test_historial_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda symbol, api_key: {
            "precio": 123.45,
            "nombre": "Apple Inc.",
            "error": None,
        },
    )
    monkeypatch.setattr(
        "bot.telegram_bot.db.obtener_historial",
        lambda chat_id, ticker: [
            (123.45, "2024-05-01 12:00"),
            (125.67, "2024-05-02 12:00"),
        ],
    )

    await historial(update, context)

    expected_message = "📜 *Historial de Apple Inc. (AAPL):*\n\n1. 123.45$ — 2024-05-01 12:00\n2. 125.67$ — 2024-05-02 12:00"
    update.message.reply_text.assert_called_once_with(expected_message, parse_mode="Markdown")


# -------------------------------
# /guardar
# -------------------------------


@pytest.mark.asyncio
async def test_guardar_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await guardar(update, context)

    update.message.reply_text.assert_called_once_with("Uso correcto: /guardar <TICKER>")


@pytest.mark.asyncio
async def test_guardar_sin_api_key(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: None)

    await guardar(update, context)

    update.message.reply_text.assert_called_once_with(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )


@pytest.mark.asyncio
async def test_guardar_error_precio(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": None, "nombre": "Apple", "error": None},
    )

    await guardar(update, context)

    update.message.reply_text.assert_called_once_with("Error: el precio recibido no es válido.")


@pytest.mark.asyncio
async def test_guardar_correcto(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda chat_id: "FAKE_API_KEY")
    monkeypatch.setattr(
        "bot.telegram_bot.fetch_stock_price",
        lambda *args: {"precio": 154.32, "nombre": "Apple Inc.", "error": None},
    )

    mock_guardar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.guardar_precio", mock_guardar)

    await guardar(update, context)

    expected = "📝 Se ha guardado el precio actual de *Apple Inc.* (AAPL) en tu historial.\n💰 Precio: 154.32 €"
    update.message.reply_text.assert_called_once_with(expected, parse_mode="Markdown")
    mock_guardar.assert_called_once_with("1", "AAPL", 154.32)


@pytest.mark.asyncio
async def test_guardar_precio_invalido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_api_key", lambda *_: "clave")
    monkeypatch.setattr("bot.telegram_bot.fetch_stock_price", lambda *_: {"error": None, "precio": "abc", "nombre": "Apple"})

    from bot.telegram_bot import guardar

    await guardar(update, context)
    update.message.reply_text.assert_called_once_with("Error: el precio recibido no es válido.")


# -------------------------------
# /borrar_historial
# -------------------------------


@pytest.mark.asyncio
async def test_borrar_historial_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await borrar_historial(update, context)

    update.message.reply_text.assert_called_once_with("Uso: /borrar_historial <TICKER>")


@pytest.mark.asyncio
async def test_borrar_historial_no_existe(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_historial", lambda chat_id, ticker: [])

    await borrar_historial(update, context)

    update.message.reply_text.assert_called_once_with("No hay historial para AAPL.")


@pytest.mark.asyncio
async def test_borrar_historial_ok(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr(
        "bot.telegram_bot.db.obtener_historial",
        lambda chat_id, ticker: [(150.0, "2024-05-17 10:00")],
    )
    mock_borrar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.borrar_historial", mock_borrar)

    await borrar_historial(update, context)

    update.message.reply_text.assert_called_once_with("🗑️ Historial de precios para AAPL eliminado.")
    mock_borrar.assert_called_once_with("1", "AAPL")


# -------------------------------
# /dejar
# -------------------------------


@pytest.mark.asyncio
async def test_dejar_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await dejar(update, context)

    update.message.reply_text.assert_called_once_with("Uso correcto: /dejar <TICKER>")


@pytest.mark.asyncio
async def test_dejar_no_seguido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    # Simula que el usuario no sigue nada
    monkeypatch.setattr("bot.telegram_bot.db.obtener_productos", lambda chat_id: [])

    await dejar(update, context)

    update.message.reply_text.assert_called_once_with("No estás siguiendo 'AAPL'.")


@pytest.mark.asyncio
async def test_dejar_ok(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    productos_seguidos = [("AAPL", 15, "Apple", 100.0, 200.0)]
    monkeypatch.setattr("bot.telegram_bot.db.obtener_productos", lambda chat_id: productos_seguidos)

    mock_eliminar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.eliminar_producto", mock_eliminar)

    await dejar(update, context)

    update.message.reply_text.assert_called_once_with("🗑️ Has dejado de seguir AAPL.")
    mock_eliminar.assert_called_once_with("1", "AAPL")


# -------------------------------
# /grafico
# -------------------------------


@pytest.mark.asyncio
async def test_grafico_sin_args():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    context = MagicMock()
    context.args = []

    await grafico(update, context)

    update.message.reply_text.assert_called_once_with("Uso: /grafico <TICKER>")


@pytest.mark.asyncio
async def test_grafico_sin_datos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.generar_grafico", lambda chat_id, ticker: None)

    await grafico(update, context)

    update.message.reply_text.assert_called_once_with("No hay historial suficiente para AAPL.")


@pytest.mark.asyncio
async def test_grafico_valido(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    # Simula un gráfico generado
    buffer_simulado = BytesIO(b"imagen_fake")
    monkeypatch.setattr("bot.telegram_bot.generar_grafico", lambda chat_id, ticker: buffer_simulado)

    await grafico(update, context)

    update.message.reply_photo.assert_called_once()
    args, kwargs = update.message.reply_photo.call_args
    assert kwargs["caption"] == "📈 Historial de precios de AAPL"


# -------------------------------
# /exportar_historial
# -------------------------------


@pytest.mark.asyncio
async def test_exportar_historial_con_ticker(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr(
        "bot.telegram_bot.db.obtener_historial_usuario",
        lambda chat_id, ticker=None: [
            {"Símbolo": "AAPL", "Precio": 150.0, "Fecha": "2024-05-23 12:00"},
        ],
    )

    from bot.telegram_bot import exportar_historial

    await exportar_historial(update, context)
    update.message.reply_document.assert_called_once()
    args, kwargs = update.message.reply_document.call_args
    assert kwargs["filename"] == "historial_AAPL.csv"


@pytest.mark.asyncio
async def test_exportar_historial_sin_datos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = []

    monkeypatch.setattr("bot.telegram_bot.db.obtener_historial_usuario", lambda chat_id, ticker=None: [])

    from bot.telegram_bot import exportar_historial

    await exportar_historial(update, context)
    update.message.reply_text.assert_called_once_with("No tienes historial de precios aún.")


@pytest.mark.asyncio
async def test_exportar_historial_sin_datos_con_ticker(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    monkeypatch.setattr("bot.telegram_bot.db.obtener_historial_usuario", lambda *_: [])

    from bot.telegram_bot import exportar_historial

    await exportar_historial(update, context)
    update.message.reply_text.assert_called_once_with("No tienes historial guardado para AAPL.")


@pytest.mark.asyncio
async def test_exportar_historial_ok(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = []

    # Simula historial para el usuario
    historial = [
        {"Símbolo": "AAPL", "Precio": 150.0, "Fecha": "2024-05-23 12:00"},
        {"Símbolo": "TSLA", "Precio": 750.0, "Fecha": "2024-05-23 13:00"},
    ]
    monkeypatch.setattr(
        "bot.telegram_bot.db.obtener_historial_usuario",
        lambda chat_id, ticker=None: historial,
    )

    from bot.telegram_bot import exportar_historial

    await exportar_historial(update, context)
    update.message.reply_document.assert_called_once()
    args, kwargs = update.message.reply_document.call_args
    assert kwargs["filename"] == "historial.csv"
    assert kwargs["caption"] == "Aquí tienes tu historial completo en formato CSV."


# -------------------------------
# /exportar_favoritas
# -------------------------------


@pytest.mark.asyncio
async def test_exportar_favoritas_sin_datos(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    monkeypatch.setattr("bot.telegram_bot.db.obtener_favoritas_usuario", lambda chat_id: [])

    from bot.telegram_bot import exportar_favoritas

    await exportar_favoritas(update, context)
    update.message.reply_text.assert_called_once_with("No estás siguiendo ninguna acción aún.")
    update.message.reply_document.assert_not_called()


@pytest.mark.asyncio
async def test_exportar_favoritas_ok(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    favoritas = [
        {
            "Símbolo": "AAPL",
            "Nombre": "Apple Inc.",
            "Intervalo (min)": 15,
            "Límite Inferior": 100,
            "Límite Superior": 200,
        }
    ]
    monkeypatch.setattr("bot.telegram_bot.db.obtener_favoritas_usuario", lambda chat_id: favoritas)

    from bot.telegram_bot import exportar_favoritas

    await exportar_favoritas(update, context)
    update.message.reply_document.assert_called_once()
    args, kwargs = update.message.reply_document.call_args
    assert kwargs["filename"] == "favoritas.csv"
    assert kwargs["caption"] == "Aquí tienes tu lista de acciones favoritas en formato CSV."


# -------------------------------
# /pedir_api_key
# -------------------------------


@pytest.mark.asyncio
async def test_pedir_api_key_con_message():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    result = await pedir_api_key(update, context)

    update.message.reply_text.assert_called_once_with(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )
    assert result == PEDIR_API_KEY


@pytest.mark.asyncio
async def test_pedir_api_key_sin_message():
    update = MagicMock(spec=Update)
    update.message = None
    context = MagicMock()

    result = await pedir_api_key(update, context)

    assert result is None


# -------------------------------
# /recibir_api_key
# -------------------------------


@pytest.mark.asyncio
async def test_recibir_api_key_sin_texto(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.text = None
    update.effective_user = MagicMock(id=1)
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    result = await recibir_api_key(update, context)

    update.message.reply_text.assert_called_once_with("❌ No he recibido ninguna API Key. Intenta de nuevo.")
    assert result is None


@pytest.mark.asyncio
async def test_recibir_api_key_valida(monkeypatch):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.text = "CLAVE123"
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()

    mock_guardar = MagicMock()
    monkeypatch.setattr("bot.telegram_bot.db.guardar_api_key", mock_guardar)

    result = await recibir_api_key(update, context)

    mock_guardar.assert_called_once_with("1", "CLAVE123")
    update.message.reply_text.assert_called_once_with(
        "✅ ¡API Key guardada correctamente! Ahora puedes usar todos los comandos del bot."
    )

    from telegram.ext import ConversationHandler

    assert result == ConversationHandler.END


@pytest.mark.asyncio
@patch("bot.telegram_bot.db.obtener_estadisticas")
async def test_media_historial_ok(mock_obtener_estadisticas):
    mock_obtener_estadisticas.return_value = (100.0, 200.0, 150.0)

    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    await media_historial(update, context)

    expected_msg = "📊 Estadísticas de AAPL en tu historial:\n\n🔻 Mínimo: 100.0 €\n🔺 Máximo: 200.0 €\n📈 Media: 150.0 €"
    update.message.reply_text.assert_called_once_with(expected_msg)


@pytest.mark.asyncio
@patch("bot.telegram_bot.db.obtener_estadisticas")
async def test_media_historial_sin_datos(mock_obtener_estadisticas):
    mock_obtener_estadisticas.return_value = None

    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)
    context = MagicMock()
    context.args = ["AAPL"]

    await media_historial(update, context)

    update.message.reply_text.assert_called_once_with("No tienes historial guardado para AAPL.")

@pytest.mark.asyncio
async def test_media_historial_sin_usuario():
    update = MagicMock(spec=Update)
    update.effective_user = None
    update.message = MagicMock()
    context = MagicMock()

    await media_historial(update, context)

@pytest.mark.asyncio
async def test_media_historial_args_invalidos():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)

    context = MagicMock()
    context.args = ["AAPL", "EXTRA"]

    await media_historial(update, context)
    update.message.reply_text.assert_called_once_with("Uso correcto: /media <TICKER>\nEjemplo: /media AAPL")

@pytest.mark.asyncio
@patch("bot.telegram_bot.db.obtener_estadisticas", side_effect=Exception("Fallo interno"))
async def test_media_historial_excepcion(mock_obtener):
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock(id=1)

    context = MagicMock()
    context.args = ["AAPL"]

    await media_historial(update, context)
    update.message.reply_text.assert_called_once_with("Ocurrió un error al calcular las estadísticas. Inténtalo más tarde.")
