from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.price_checker import get_alert_message, get_help_text
from bot.user_session import login, logout, is_logged_in
from bot.historial import obtener_historial
from bot.alerts import registrar_alerta, gestionar_alertas
from bot.seguimiento import seguir_accion, dejar_de_seguir, obtener_favoritas
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mensaje = f"👋 ¡Hola {user.first_name}!\n"
    if is_logged_in(user.id):
        mensaje += "Estás logueado. Usa /comandos para ver lo que puedes hacer."
    else:
        mensaje += "Para comenzar, usa /login para iniciar sesión."
    await update.message.reply_text(mensaje)

# /comandos
async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_help_text())

# /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Para ver todas las opciones disponibles escribe /comandos")

# /price <TICKER>
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Uso correcto: /price TICKER")
        return
    ticker = context.args[0].upper()
    msg = get_alert_message(ticker)
    await update.message.reply_text(msg)

# /portfolio
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Aquí estaría tu portafolio. (Función en desarrollo)")

# /login
async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login(update.effective_user.id)
    await update.message.reply_text("✅ Sesión iniciada.")

# /logout
async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logout(update.effective_user.id)
    await update.message.reply_text("🔒 Sesión cerrada.")

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
    precios = obtener_historial(ticker)
    if precios:
        historial_str = "\n".join([f"{i+1}. {p}€" for i, p in enumerate(precios)])
        await update.message.reply_text(f"📜 Historial de {ticker}:\n{historial_str}")
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
    try:
        intervalo = int(context.args[1]) * 60
        min_price = float(context.args[2])
        max_price = float(context.args[3])
    except ValueError:
        await update.message.reply_text("❗ Intervalo y precios deben ser numéricos.")
        return
    registrar_alerta(update.effective_user.id, ticker, intervalo, min_price, max_price)
    await update.message.reply_text(
        f"🔔 Alerta para {ticker} cada {intervalo // 60} minutos.\n"
        f"Rango de alerta: {min_price} € - {max_price} €"
    )

# /seguir <TICKER>
async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(update.effective_user.id):
        await update.message.reply_text("Debes hacer /login para seguir acciones.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /seguir <TICKER>")
        return
    ticker = context.args[0].upper()
    seguir_accion(update.effective_user.id, ticker)
    await update.message.reply_text(f"🔖 Ahora estás siguiendo {ticker}.")

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

# /favoritas
async def favoritas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(update.effective_user.id):
        await update.message.reply_text("Debes hacer /login para ver tus favoritas.")
        return
    favoritas = obtener_favoritas(update.effective_user.id)
    if favoritas:
        await update.message.reply_text("⭐ Acciones que estás siguiendo:\n" + "\n".join(favoritas))
    else:
        await update.message.reply_text("Aún no estás siguiendo ninguna acción.")

# MAIN
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("comandos", comandos))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("login", login_cmd))
    app.add_handler(CommandHandler("logout", logout_cmd))
    app.add_handler(CommandHandler("acciones", acciones))
    app.add_handler(CommandHandler("historial", historial))
    app.add_handler(CommandHandler("alerta", alerta))
    app.add_handler(CommandHandler("seguir", seguir))
    app.add_handler(CommandHandler("dejar", dejar))
    app.add_handler(CommandHandler("favoritas", favoritas))

    app.job_queue.run_once(lambda *_: asyncio.create_task(gestionar_alertas(app)), 0)

    print("✅ Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
