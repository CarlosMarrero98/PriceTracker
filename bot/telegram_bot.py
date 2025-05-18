from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.db_manager import DatabaseManager
from bot.mensajes_ayuda import get_commands_text, get_help_text
from bot.get_price import fetch_stock_price

from bot.user_session import login, logout, is_logged_in
from bot.historial import obtener_historial
from bot.alerts import registrar_alerta, gestionar_alertas
from bot.seguimiento import dejar_de_seguir, obtener_favoritas
from bot.grafico import generar_grafico
import os
import asyncio

from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

db = DatabaseManager()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registra al usuario en la base de datos y envía mensaje de bienvenida.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    user = update.effective_user
    if user is None or update.message is None:
        return
    
    chat_id = str(user.id)
    username = user.username or "sin_nombre"

    db.agregar_usuario(chat_id, username)

    mensaje = f"¡Hola {user.first_name}!\n"
    mensaje += "Soy tu asistente para seguir precios de acciones y recibir alertas.\n\n"
    mensaje += "Para empezar, usa el comando /comandos para ver lo que puedo hacer.\n"

    await update.message.reply_text(mensaje)

# /comandos
async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envía un mensaje con la lista de comandos disponibles.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message:
        await update.message.reply_text(get_commands_text(), parse_mode="Markdown")

# /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Proporciona un mensaje de ayuda explicando cómo usar el bot.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto de ejecución del bot.
    """
    if update.message:
        await update.message.reply_text(get_help_text(), parse_mode="Markdown")

# /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]
async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Permite al usuario seguir una acción bursátil y establecer alertas.

    Sintaxis esperada: /seguir <TICKER> [INTERVALO] [LIMITE_INF] [LIMITE_SUP]

    Args:
        update (Update): Objeto de actualización de Telegram.
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

    # Valores por defecto
    intervalo = 3600  # 1 hora
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
            "Intervalo y límites deben ser validos."
        )
        return
    
    api_key = os.getenv("TWELVE_API_KEY")
    if not api_key:
        await update.message.reply_text(
            "Error interno: clave de API no configurada."
        )
        return
    
    data = fetch_stock_price(ticker, api_key)

    if data["error"] or data["nombre"] is None:
        await update.message.reply_text(
            f"No se pudo seguir '{ticker}': {data['error'] or 'Error desconocido'}"
        )
        return
    
    # Guardar en base de datos
    nombre_empresa = data["nombre"]
    assert isinstance(nombre_empresa, str), "Nombre de empresa no válido"

    db.agregar_producto(
        chat_id, ticker, nombre_empresa, intervalo, limite_inf, limite_sup
    )

    await update.message.reply_text(
        f"✅ Ahora estás siguiendo {data['nombre']} ({ticker}) cada {intervalo} minutos.\n"
        f"🔔 Límites configurados: {limite_inf}$ - {limite_sup}$"
    )

# /favoritas
async def favoritas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra la lista de acciones que el usuario está siguiendo.

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

# /price <TICKER>
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responde con el precio actual de una acción especificada por su ticker.

    El usuario debe proporcionar el símbolo bursátil como argumento. Si el ticker no es válido
    o no hay clave de API, se informa del error.

    Args:
        update (Update): Objeto de actualización de Telegram.
        context (ContextTypes.DEFAULT_TYPE): Contexto que incluye argumentos y metadatos del bot.
    """
    if update.effective_user is None or update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Uso correcto: /price <TICKER>")
        return

    ticker = context.args[0].strip().upper()
    api_key = os.getenv("TWELVE_API_KEY")

    if not api_key:
        await update.message.reply_text(
            "Error: no se ha configurado la clave de la API."
        )
        return

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









# /portfolio
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Aquí estaría tu portafolio. (Función en desarrollo)")

# /acciones
async def acciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ejemplos = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    await update.message.reply_text("📈 Acciones populares:\n" + "\n".join(ejemplos))

# /historial <TICKER>
async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /historial TICKER")
        return

    ticker = context.args[0].upper()
    data = fetch_stock_price(ticker)
    if not data:
        await update.message.reply_text(f"❌ Ticker '{ticker}' no válido o no disponible.")
        return

    precios = obtener_historial(ticker)
    if precios:
        historial_str = "\n".join([f"{i+1}. {p}€" for i, p in enumerate(precios)])
        await update.message.reply_text(
            f"📜 Historial de {data['name']} ({ticker}):\n{historial_str}"
        )
    else:
        await update.message.reply_text(f"No hay historial para {ticker}.")

# /alerta <TICKER> <MINUTOS> <MIN_PRECIO> <MAX_PRECIO>
async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(update.effective_user.id):
        await update.message.reply_text("Debes hacer /login primero.")
        return
    if len(context.args) != 4:
        await update.message.reply_text("Uso: /alerta <TICKER> <MINUTOS> <MIN_PRECIO> <MAX_PRECIO>")
        return

    ticker = context.args[0].upper()

    if not validate_ticker(ticker):
        await update.message.reply_text(f"❌ El ticker '{ticker}' no es válido.")
        return

    try:
        intervalo = int(context.args[1]) * 60
        min_price = float(context.args[2])
        max_price = float(context.args[3])
    except ValueError:
        await update.message.reply_text("❗ Intervalo y precios deben ser numéricos.")
        return

    data = fetch_stock_price(ticker)
    registrar_alerta(update.effective_user.id, ticker, intervalo, min_price, max_price)
    await update.message.reply_text(
        f"🔔 Alerta para {data['name']} ({ticker}) cada {intervalo // 60} minutos.\n"
        f"Rango de alerta: {min_price} € - {max_price} €"
    )



# /dejar <TICKER>
async def dejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(update.effective_user.id):
        await update.message.reply_text("Debes hacer /login para dejar de seguir acciones.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /dejar <TICKER>")
        return
    ticker = context.args[0].upper()
    dejar_de_seguir(update.effective_user.id, ticker)
    await update.message.reply_text(f"❌ Has dejado de seguir {ticker}.")

# /grafico <TICKER>
async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /grafico <TICKER>")
        return
    ticker = context.args[0].upper()
    data = fetch_stock_price(ticker)
    if not data:
        await update.message.reply_text(f"❌ El ticker '{ticker}' no es válido.")
        return
    buffer = generar_grafico(ticker)
    if not buffer:
        await update.message.reply_text(f"No hay historial suficiente para {ticker}.")
        return
    await update.message.reply_photo(photo=InputFile(buffer), caption=f"📈 Historial de precios de {data['name']} ({ticker})")

# MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("comandos", comandos))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("acciones", acciones))
    app.add_handler(CommandHandler("seguir", seguir))
    app.add_handler(CommandHandler("favoritas", favoritas))


    app.job_queue.run_once(lambda *_: asyncio.create_task(gestionar_alertas(app)), 0)

    print("✅ Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
