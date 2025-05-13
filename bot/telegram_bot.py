import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USERS = {}
ACCIONES = {}
FRECUENCIA = {}

# ----- Comandos -----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Bienvenido al bot de inversiones! Usa /login para comenzar.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USERS[user_id] = True
    await update.message.reply_text("Sesión iniciada. ¿Qué acciones deseas seguir? Usa /acciones para configurarlo.")

async def acciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if USERS.get(user_id):
        await update.message.reply_text("Escribe los tickers separados por coma (ej: TSLA, AAPL):")
        return 1
    await update.message.reply_text("Primero debes iniciar sesión con /login.")
    return ConversationHandler.END

async def guardar_acciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.upper().replace(" ", "")
    ACCIONES[user_id] = texto.split(",")
    await update.message.reply_text(f"Acciones guardadas: {ACCIONES[user_id]}")
    return ConversationHandler.END

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /price TICKER")
        return
    ticker = context.args[0].upper()
    precio = get_price_from_tuelvedata(ticker)
    await update.message.reply_text(f"El precio actual de {ticker} es {precio}€")

async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funcionalidad de alerta guardada. (A implementar)")

async def frecuencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Uso: /frecuencia MINUTOS")
        return
    try:
        minutos = int(context.args[0])
        FRECUENCIA[user_id] = minutos
        await update.message.reply_text(f"Consultaré precios cada {minutos} minutos.")
    except ValueError:
        await update.message.reply_text("Introduce un número válido.")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USERS.pop(user_id, None)
    await update.message.reply_text("Sesión cerrada.")

# ----- Lógica de simulación -----

def get_price_from_tuelvedata(ticker: str) -> float:
    import random
    return round(random.uniform(100, 500), 2)

async def job_check_prices(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    for user_id in USERS:
        if user_id in ACCIONES:
            for ticker in ACCIONES[user_id]:
                precio = get_price_from_tuelvedata(ticker)
                await app.bot.send_message(chat_id=user_id, text=f"📈 {ticker} = {precio}€")

# ----- Main -----

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("acciones", acciones)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_acciones)]},
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("alert", alert))
    app.add_handler(CommandHandler("frecuencia", frecuencia))
    app.add_handler(CommandHandler("logout", logout))

    # Comprobaciones periódicas
    app.job_queue.run_repeating(job_check_prices, interval=60, first=10)

    print("Bot iniciado")
    app.run_polling()

if __name__ == "__main__":
    main()

