"""
Módulo: telegram_bot.py

Contiene los comandos principales del bot de Telegram para el proyecto PriceTracker.
Incluye funciones para registrar usuarios, gestionar acciones seguidas,
consultar precios, exportar historiales, generar gráficos y más.

Diseñado para integrarse con python-telegram-bot y una base de datos SQLite.
"""

import io

import pandas as pd
from telegram import InputFile, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from bot.db_instance import db
from bot.get_price import fetch_stock_price
from bot.grafico import generar_grafico
from bot.mensajes_ayuda import get_commands_text, get_help_text

PEDIR_API_KEY = 1

# ==================== EXPORTAR HISTORIAL CSV (todo o por ticker) ====================


async def exportar_historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Exporta el historial de precios del usuario a un archivo CSV.

    Args:
        update (telegram.Update): Contiene el mensaje recibido.
        context (telegram.ext.CallbackContext): Contexto con argumentos opcionales.

    Returns:
        None
    """
    if update.effective_user is None or update.message is None:
        return

    chat_id = str(update.effective_user.id)
    # Compatibilidad con tests: asegúrate de que context.args siempre es lista
    args = list(context.args) if hasattr(context, "args") and isinstance(context.args, list | tuple) else []
    ticker = args[0].strip().upper() if args else None

    # Obtiene historial (todo o filtrado)
    historial = db.obtener_historial_usuario(chat_id, ticker)

    # Si no hay historial, envía mensaje adecuado según si se filtró por ticker
    if not historial:
        if ticker:
            await update.message.reply_text(f"No tienes historial guardado para {ticker}.")
        else:
            await update.message.reply_text("No tienes historial de precios aún.")
        return

    # Prepara el archivo CSV en memoria
    nombre_archivo = f"historial_{ticker}.csv" if ticker else "historial.csv"
    df = pd.DataFrame(historial)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Envía el archivo CSV al usuario
    await update.message.reply_document(
        document=InputFile(io.BytesIO(buffer.getvalue().encode()), filename=nombre_archivo),
        filename=nombre_archivo,
        caption=f"Aquí tienes tu historial {'de ' + ticker if ticker else 'completo'} en formato CSV.",
    )


# ==================== EXPORTAR FAVORITAS CSV ====================


async def exportar_favoritas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Exporta la lista de acciones favoritas del usuario a un archivo CSV.

    Args:
        update (telegram.Update): Contiene el mensaje recibido.
        context (telegram.ext.CallbackContext): Contexto del bot.

    Returns:
        None
    """
    if update.effective_user is None or update.message is None:
        return

    chat_id = str(update.effective_user.id)
    favoritas = db.obtener_favoritas_usuario(chat_id)

    if not favoritas:
        await update.message.reply_text("No estás siguiendo ninguna acción aún.")
        return

    # Prepara y envía el archivo CSV
    df = pd.DataFrame(favoritas)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    await update.message.reply_document(
        document=InputFile(io.BytesIO(buffer.getvalue().encode()), filename="favoritas.csv"),
        filename="favoritas.csv",
        caption="Aquí tienes tu lista de acciones favoritas en formato CSV.",
    )


# ==================== PETICIÓN Y GESTIÓN DE API KEY ====================


async def pedir_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """
    Solicita al usuario que introduzca su API Key de TwelveData.

    Args:
        update (telegram.Update): Objeto con el mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto del comando.

    Returns:
        int | None: Estado de la conversación para continuar o None si falla.
    """
    if update.message is None:
        return None

    await update.message.reply_text(
        "🔑 Antes de continuar, necesito tu API Key de TwelveData para poder consultar precios.\n"
        "Puedes obtener una gratis en https://twelvedata.com/. Envíamela ahora:"
    )
    return PEDIR_API_KEY


async def recibir_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """
    Guarda la API Key proporcionada por el usuario y termina la conversación.

    Args:
        update (telegram.Update): Mensaje que contiene la API Key.
        context (telegram.ext.CallbackContext): Contexto de la conversación.

    Returns:
        int | None: Finalización del flujo de conversación o None si hubo error.
    """
    if update.effective_user is None or update.message is None:
        return None

    chat_id = str(update.effective_user.id)
    text = update.message.text

    if text is None:
        await update.message.reply_text("❌ No he recibido ninguna API Key. Intenta de nuevo.")
        return None

    api_key = text.strip()
    db.guardar_api_key(chat_id, api_key)

    await update.message.reply_text("✅ ¡API Key guardada correctamente! Ahora puedes usar todos los comandos del bot.")
    return ConversationHandler.END


# ==================== COMANDOS PRINCIPALES DEL BOT ====================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """
    Registra un nuevo usuario y envía un mensaje de bienvenida.

    Si el usuario no tiene una API Key registrada, solicita que la introduzca.

    Args:
        update (telegram.Update): Objeto que contiene el mensaje recibido.
        context (telegram.ext.CallbackContext): Contexto de ejecución del comando.

    Returns:
        int | None: Estado de la conversación si se inicia captura de API Key, o None.
    """
    user = update.effective_user
    if user is None or update.message is None:
        return None

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

    return None


async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envía la lista de comandos disponibles al usuario.

    Args:
        update (telegram.Update): Objeto con el mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto que puede incluir argumentos.

    Returns:
        None
    """
    if update.message:
        await update.message.reply_text(get_commands_text(), parse_mode="Markdown")


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra un mensaje de ayuda detallada con ejemplos de uso para cada comando del bot.

    Args:
        update (telegram.Update): Objeto con el mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto que puede incluir argumentos.

    Returns:
        None
    """
    if update.message:
        await update.message.reply_text(get_help_text(), parse_mode="Markdown")


# ==================== SEGUIMIENTO Y FAVORITOS ====================


async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Registra un nuevo seguimiento de un activo financiero para el usuario.

    Parámetros opcionales: intervalo de revisión (minutos), límite inferior y superior.

    Args:
        update (telegram.Update): Objeto con el mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto que puede incluir argumentos.

    Returns:
        None
    """
    if update.message is None or update.effective_user is None:
        return

    if not context.args:
        await update.message.reply_text("Uso: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)
    intervalo = 3600  # Por defecto, 1 hora
    limite_inf = 0.0
    limite_sup = 0.0

    # Procesa los argumentos opcionales
    try:
        if len(context.args) >= 2:
            intervalo = int(context.args[1])
        if len(context.args) >= 4:
            limite_inf = float(context.args[2])
            limite_sup = float(context.args[3])
    except ValueError:
        await update.message.reply_text("Intervalo y límites deben ser válidos.")
        return

    api_key = db.obtener_api_key(chat_id)
    if not api_key:
        await pedir_api_key(update, context)
        return

    data = fetch_stock_price(ticker, api_key)
    if data["error"] or data["nombre"] is None:
        await update.message.reply_text(f"No se pudo seguir '{ticker}': {data['error'] or 'Error desconocido'}")
        return

    nombre_empresa = data["nombre"]
    assert isinstance(nombre_empresa, str), "Nombre de empresa no válido"

    db.agregar_producto(chat_id, ticker, nombre_empresa, intervalo, limite_inf, limite_sup)

    await update.message.reply_text(
        f"✅ Ahora estás siguiendo {data['nombre']} ({ticker}) cada {intervalo} minutos.\n"
        f"🔔 Límites configurados: {limite_inf}$ - {limite_sup}$"
    )


async def favoritas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Lista todas las acciones favoritas seguidas por el usuario.

    Args:
        update (telegram.Update): Contiene el mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto del bot.

    Returns:
        None
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
            f"📈 *{nombre}* ({symbol})\n⏱️ Revisión cada {intervalo} min\n🔔 Límites: {limite_inf}$ - {limite_sup}$\n\n"
        )
    await update.message.reply_text(mensaje.strip(), parse_mode="Markdown")


# ==================== CONSULTA DE PRECIOS Y GUARDADO ====================


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Consulta y muestra el precio actual de un activo financiero.

    Args:
        update (telegram.Update): Contiene el comando /price recibido.
        context (telegram.ext.CallbackContext): Contexto con posibles argumentos.

    Returns:
        None
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
        await pedir_api_key(update, context)
        return

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(f"No se pudo obtener el precio de '{ticker}': {data['error']}")
        return

    nombre = data["nombre"]
    precio = data["precio"]

    await update.message.reply_text(
        f"📈 *{nombre}* ({ticker})\n💰 Precio actual: {precio:.2f}$",
        parse_mode="Markdown",
    )


async def guardar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Guarda el precio actual de una acción en el historial del usuario.

    Args:
        update (telegram.Update): Mensaje del usuario.
        context (telegram.ext.CallbackContext): Contexto del bot.

    Returns:
        None
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
        await pedir_api_key(update, context)
        return

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(f"No se pudo obtener el precio de '{ticker}': {data['error']}")
        return

    precio = data["precio"]
    nombre = data["nombre"]

    if not isinstance(precio, float):
        await update.message.reply_text("Error: el precio recibido no es válido.")
        return

    db.guardar_precio(chat_id, ticker, precio)

    await update.message.reply_text(
        f"📝 Se ha guardado el precio actual de *{nombre}* ({ticker}) en tu historial.\n💰 Precio: {precio:.2f} €",
        parse_mode="Markdown",
    )


# ==================== HISTORIAL DE PRECIOS Y GESTIÓN ====================


async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Devuelve el historial de precios guardado para una acción del usuario.

    Args:
        update (telegram.Update): Comando recibido del usuario.
        context (telegram.ext.CallbackContext): Argumentos con el ticker.

    Returns:
        None
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
        await pedir_api_key(update, context)
        return

    data = fetch_stock_price(ticker, api_key)
    if data["error"]:
        await update.message.reply_text(f"Ticker '{ticker}' no válido o no disponible: {data['error']}")
        return

    historial = db.obtener_historial(chat_id, ticker)
    if not historial:
        await update.message.reply_text(f"📭 No hay historial guardado para {ticker}.")
        return

    historial_str = "\n".join([f"{i + 1}. {precio:.2f}$ — {timestamp}" for i, (precio, timestamp) in enumerate(historial)])

    await update.message.reply_text(
        f"📜 *Historial de {data['nombre']} ({ticker}):*\n\n{historial_str}",
        parse_mode="Markdown",
    )


async def borrar_historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Elimina todo el historial de precios de una acción para el usuario.

    Args:
        update (telegram.Update): Mensaje recibido del usuario.
        context (telegram.ext.CallbackContext): Argumentos del bot.

    Returns:
        None
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


# ==================== GESTIÓN DE ACCIONES FAVORITAS ====================


async def dejar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Permite al usuario dejar de seguir una acción.

    Args:
        update (telegram.Update): Contiene el comando recibido.
        context (telegram.ext.CallbackContext): Argumentos del comando.

    Returns:
        None
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


# ==================== GRÁFICO DEL HISTORIAL DE PRECIOS ====================


async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Genera y envía un gráfico PNG del historial de precios del usuario para una acción.

    Args:
        update (telegram.Update): Objeto con el comando recibido.
        context (telegram.ext.CallbackContext): Contexto de argumentos.

    Returns:
        None
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

    await update.message.reply_photo(photo=InputFile(buffer), caption=f"📈 Historial de precios de {ticker}")


# ==================== MEDIA DEL HISTORIAL ====================


async def media_historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Calcula y muestra estadísticas básicas (mínimo, máximo, media) del historial de precios.

    Args:
        update (telegram.Update): Contiene el mensaje del usuario.
        context (telegram.ext.CallbackContext): Argumentos con el ticker solicitado.

    Returns:
        None
    """
    if update.effective_user is None or update.message is None:
        return

    if len(context.args) != 1:
        await update.message.reply_text("Uso correcto: /media <TICKER>\nEjemplo: /media AAPL")
        return

    ticker = context.args[0].strip().upper()
    chat_id = str(update.effective_user.id)

    try:
        resultado = db.obtener_estadisticas(chat_id, ticker)

        if resultado is None:
            await update.message.reply_text(f"No tienes historial guardado para {ticker}.")
            return

        minimo, maximo, media = resultado

        minimo = round(minimo, 2)
        maximo = round(maximo, 2)
        media = round(media, 2)

        print(f"Estadísticas de {ticker}: min={minimo}, max={maximo}, media={media}")

        await update.message.reply_text(
            f"📊 Estadísticas de {ticker} en tu historial:\n\n"
            f"🔻 Mínimo: {minimo} €\n"
            f"🔺 Máximo: {maximo} €\n"
            f"📈 Media: {media} €"
        )

    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        await update.message.reply_text("Ocurrió un error al calcular las estadísticas. Inténtalo más tarde.")
