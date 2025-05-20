from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from bot.mensajes_ayuda import get_commands_text, get_help_text
from bot.get_price import fetch_stock_price
from bot.grafico import generar_grafico
from bot.db_instance import db
import os

PEDIR_API_KEY = 1

async def pedir_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Solicita la API Key de TwelveData al usuario si no la tiene registrada.

    Args:
        update (Update): Objeto de actualización de Telegram recibido por el bot.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    Returns:
        int: Estado de la conversación (PEDIR_API_KEY).
    """
    await update.message.reply_text(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )
    return PEDIR_API_KEY

async def recibir_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe y guarda la API Key enviada por el usuario, asociándola a su chat_id.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    Returns:
        int: Finaliza el estado conversacional tras guardar la clave.
    """
    chat_id = str(update.effective_user.id)
    api_key = update.message.text.strip()
    db.guardar_api_key(chat_id, api_key)
    await update.message.reply_text(
        "✅ ¡API Key guardada correctamente! Ahora puedes usar todos los comandos del bot."
    )
    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registra al usuario en la base de datos y gestiona la petición de API Key si no está registrada.

    Si el usuario no tiene clave, la solicita y entra en el estado conversacional adecuado.

    Args:
        update (Update): Objeto de actualización de Telegram recibido por el bot.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    Returns:
        int or None: Retorna el siguiente estado si es necesario pedir la API Key.
    """
    user = update.effective_user
    if user is None or update.message is None:
        return

    chat_id = str(user.id)
    username = user.username or "sin_nombre"
    db.agregar_usuario(chat_id, username)
    api_key = db.obtener_api_key(chat_id)

    if not api_key:
        return await pedir_api_key(update, context)

    mensaje = (
        f"¡Hola {user.first_name}!\n"
        "Soy tu asistente para seguir precios de acciones y recibir alertas.\n\n"
        "Para empezar, usa el comando /comandos para ver lo que puedo hacer.\n"
    )
    await update.message.reply_text(mensaje)

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envía un mensaje con la lista de comandos disponibles y sus descripciones.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message:
        await update.message.reply_text(get_commands_text(), parse_mode="Markdown")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Proporciona un mensaje de ayuda explicando cómo usar el bot y sus funcionalidades básicas.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message:
        await update.message.reply_text(get_help_text(), parse_mode="Markdown")

async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Permite al usuario seguir una acción bursátil y establecer alertas personalizadas.

    Sintaxis esperada: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]

    Args:
        update (Update): Objeto de actualización de Telegram recibido por el bot.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message is None or update.effective_user is None:
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]"
        )
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    intervalo = 3600  # Por defecto, 1 hora
    limite_inf = 0.0
    limite_sup = 0.0

    try:
        if len(context.args) >= 2:
            intervalo = int(context.args[1])
        if len(context.args) >= 4:
            limite_inf = float(context.args[2])
            limite_sup = float(context.args[3])
    except ValueError:
        await update.message.reply_text(
            "Intervalo y límites deben ser válidos."
        )
        return

    api_key = db.obtener_api_key(chat_id)
    if not api_key:
        return await pedir_api_key(update, context)

    data = fetch_stock_price(ticker, api_key)
    if data["error"] or data["nombre"] is None:
        await update.message.reply_text(
            f"No se pudo seguir '{ticker}': {data['error'] or 'Error desconocido'}"
        )
        return

    nombre_empresa = data["nombre"]
    assert isinstance(nombre_empresa, str), "Nombre de empresa no válido"

    db.agregar_producto(
        chat_id, ticker, nombre_empresa, intervalo, limite_inf, limite_sup
    )

    await update.message.reply_text(
        f"✅ Ahora estás siguiendo {data['nombre']} ({ticker}) cada {intervalo} minutos.\n"
        f"🔔 Límites configurados: {limite_inf}$ - {limite_sup}$"
    )

async def favoritas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la lista de acciones que el usuario está siguiendo, incluyendo intervalos y límites configurados.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message is None or update.effective_user is None:
        return

    chat_id = str(update.effective_user.id)
    productos = db.obtener_productos(chat_id)

    if not productos:
        await update.message.reply_text("Aún no estás siguiendo ninguna acción.")
        return

    mensaje = "⭐ *Tus acciones favoritas:*\n\n"
    for symbol, intervalo, nombre, limite_inf, limite_sup in productos:
        mensaje += (
            f"📈 *{nombre}* ({symbol})\n"
            f"⏱️ Revisión cada {intervalo} min\n"
            f"🔔 Límites: {limite_inf}$ - {limite_sup}$\n\n"
        )
    await update.message.reply_text(mensaje.strip(), parse_mode="Markdown")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde con el precio actual de una acción especificada por su ticker.

    Args:
        update (Update): Objeto de actualización de Telegram recibido por el bot.
        context (ContextTypes.DEFAULT_TYPE): Contexto con argumentos y datos del usuario.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso correcto: /price <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    api_key = db.obtener_api_key(chat_id)
    if not api_key:
        return await pedir_api_key(update, context)

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(
            f"No se pudo obtener el precio de '{ticker}': {data['error']}"
        )
        return

    nombre = data["nombre"]
    precio = data["precio"]

    await update.message.reply_text(
        f"📈 *{nombre}* ({ticker})\n💰 Precio actual: {precio:.2f}$",
        parse_mode="Markdown",
    )

async def guardar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guarda el precio actual de una acción en el historial del usuario.

    El usuario debe indicar el símbolo bursátil como argumento. Se consulta el precio
    mediante la API y se almacena en la base de datos si es válido.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto que incluye argumentos del comando.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso correcto: /guardar <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    api_key = db.obtener_api_key(chat_id)
    if not api_key:
        return await pedir_api_key(update, context)

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(
            f"No se pudo obtener el precio de '{ticker}': {data['error']}"
        )
        return

    precio = data["precio"]
    nombre = data["nombre"]

    if not isinstance(precio, float):
        await update.message.reply_text("Error: el precio recibido no es válido.")
        return

    db.guardar_precio(chat_id, ticker, precio)

    await update.message.reply_text(
        f"📝 Se ha guardado el precio actual de *{nombre}* ({ticker}) en tu historial.\n"
        f"💰 Precio: {precio:.2f} €",
        parse_mode="Markdown",
    )

async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra los últimos precios guardados para una acción seguida por el usuario.

    El usuario debe indicar el símbolo bursátil como argumento. Se verifica la validez del ticker
    usando la API y luego se recupera el historial desde la base de datos. Si no hay historial
    o el ticker no es válido, se informa al usuario.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto con argumentos del comando.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso correcto: /historial <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    api_key = db.obtener_api_key(chat_id)
    if not api_key:
        return await pedir_api_key(update, context)

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(
            f"Ticker '{ticker}' no válido o no disponible: {data['error']}"
        )
        return

    historial = db.obtener_historial(chat_id, ticker)
    if not historial:
        await update.message.reply_text(f"📭 No hay historial guardado para {ticker}.")
        return

    historial_str = "\n".join(
        [
            f"{i + 1}. {precio:.2f}$ — {timestamp}"
            for i, (precio, timestamp) in enumerate(historial)
        ]
    )

    await update.message.reply_text(
        f"📜 *Historial de {data['nombre']} ({ticker}):*\n\n{historial_str}",
        parse_mode="Markdown",
    )

async def borrar_historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Elimina el historial de precios de un activo para el usuario actual.

    El usuario debe proporcionar el símbolo bursátil como argumento. Si existe historial,
    se borra y se informa. Si no, se notifica que no hay datos.

    Args:
        update (Update): Objeto de actualización recibido por el bot.
        context (ContextTypes.DEFAULT_TYPE): Contexto que contiene los argumentos.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso: /borrar_historial <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)

    historial = db.obtener_historial(chat_id, ticker)
    if not historial:
        await update.message.reply_text(f"No hay historial para {ticker}.")
        return

    db.borrar_historial(chat_id, ticker)
    await update.message.reply_text(f"🗑️ Historial de precios para {ticker} eliminado.")

async def dejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Elimina un activo de la lista de seguimiento del usuario.

    El usuario debe indicar el símbolo bursátil. Si no lo está siguiendo, se le informa.
    Si lo está, se elimina de la base de datos y se notifica la acción.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto con los argumentos del comando.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso correcto: /dejar <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    productos = db.obtener_productos(chat_id)
    seguidos = [p[0] for p in productos]

    if ticker not in seguidos:
        await update.message.reply_text(f"No estás siguiendo '{ticker}'.")
        return

    db.eliminar_producto(chat_id, ticker)
    await update.message.reply_text(f"🗑️ Has dejado de seguir {ticker}.")

async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Genera y envía un gráfico con el historial de precios del activo indicado.

    El usuario debe especificar un ticker. Si hay datos históricos suficientes,
    se genera un gráfico y se envía como imagen. En caso contrario, se notifica
    que no hay historial disponible.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto que incluye los argumentos del comando.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso: /grafico <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    buffer = generar_grafico(chat_id, ticker)

    if not buffer:
        await update.message.reply_text(f"No hay historial suficiente para {ticker}.")
        return

    await update.message.reply_photo(
        photo=InputFile(buffer), caption=f"📈 Historial de precios de {ticker}"
    )
