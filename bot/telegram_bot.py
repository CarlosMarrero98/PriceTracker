from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.price_checker import get_alert_message, get_help_text
from bot.user_session import login, logout, is_logged_in
from bot.historial import obtener_historial
from bot.alerts import registrar_alerta, gestionar_alertas
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Comando /start con aviso de login
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mensaje = f"👋 ¡Hola {user.first_name}!\n"

    if is_logged_in(user.id):
        mensaje += "Estás logueado. Usa /comandos para ver lo que puedes hacer."
    else:
        mensaje += "Para comenzar, usa /login para iniciar sesión."

    await update.message.reply_text(mensaje)

# Comando /comandos
async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_help_text())

# Comando /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Para ver todas las opciones disponibles escribe /comandos")

# Comando /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Uso correcto: /price TICKER")
        return
    ticker = context.args[0].upper()
    msg = get_alert_message(ticker)
    await update.message.reply_text(msg)

# Comando /portfolio
async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Aquí estaría tu portafolio. (Función en desarrollo)")

# Comando /login
async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login(update.effective_user.id)
    await update.message.reply_text("✅ Sesión iniciada.")

# Comando /logout
async def logout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logout(update.effective_user.id)
    await update.message.reply_text("🔒 Sesión cerrada.")

# Comando /acciones
async def acciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ejemplos = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    await update.message.reply_text("📈 Acciones populares:\n" + "\n".join(ejemplos))

# Comando /historial
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

# Comando /alerta
async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_logged_in(update.effective_user.id):
        await update.message.reply_text("Debes hacer /login primero.")
        return
    if len(context.args) != 2:
        await update.message.reply_text("Uso: /alerta <TICKER> <MINUTOS>")
        return
    ticker = context.args[0].upper()
    try:
        intervalo = int(context.args[1]) * 60
    except ValueError:
        await update.message.reply_text("❗ Intervalo debe ser un número entero.")
        return
    registrar_alerta(update.effective_user.id, ticker, intervalo)
    await update.message.reply_text(f"🔔 Alerta para {ticker} cada {intervalo // 60} minutos activada.")

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

    app.job_queue.run_once(lambda *_: asyncio.create_task(gestionar_alertas(app)), 0)

    print("✅ Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
