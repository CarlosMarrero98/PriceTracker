from bot.telegram_bot import (
    start,
    comandos,
    ayuda,
    seguir,
    favoritas,
    price,
    guardar,
    historial,
    borrar_historial,
    dejar,
    grafico,
    recibir_api_key,
    PEDIR_API_KEY,
)
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.seguimiento import lanzar_seguimiento
import os

load_dotenv()

def prueba_telegram_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).post_init(lanzar_seguimiento).build()

    # Handler conversacional para el flujo de la API Key
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PEDIR_API_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_api_key)
            ],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    # El resto de tus handlers
    app.add_handler(CommandHandler("comandos", comandos))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("seguir", seguir))
    app.add_handler(CommandHandler("favoritas", favoritas))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("guardar", guardar))
    app.add_handler(CommandHandler("historial", historial))
    app.add_handler(CommandHandler("borrar_historial", borrar_historial))
    app.add_handler(CommandHandler("dejar", dejar))
    app.add_handler(CommandHandler("grafico", grafico))

    print("✅ Bot iniciado.")
    app.run_polling()

def main():
    prueba_telegram_bot()

if __name__ == "__main__":
    main()
