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
    exportar_historial,    
    exportar_favoritas,   
)
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.seguimiento import comprobar_alertas_periodicamente
import asyncio
import os

load_dotenv()

def prueba_telegram_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Se ejecuta justo después de iniciar el bot
    async def post_init(app):
        global seguimiento_task
        seguimiento_task = asyncio.create_task(comprobar_alertas_periodicamente(app))

    # Se ejecuta justo antes de cerrar el bot
    async def post_shutdown(app):
        global seguimiento_task
        if seguimiento_task:
            seguimiento_task.cancel()
            try:
                await seguimiento_task
            except asyncio.CancelledError:
                print("🛑 Tarea de seguimiento detenida correctamente.")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

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

    # Comandos del bot
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
    app.add_handler(CommandHandler("exportar_historial", exportar_historial))
    app.add_handler(CommandHandler("exportar_favoritas", exportar_favoritas))  

    print("✅ Bot iniciado.")
    app.run_polling()

def main():
    prueba_telegram_bot()

if __name__ == "__main__":
    main()
