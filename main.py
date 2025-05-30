import asyncio
import os
from typing import Any

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.seguimiento import comprobar_alertas_periodicamente
from bot.telegram_bot import (
    PEDIR_API_KEY,
    ayuda,
    borrar_historial,
    comandos,
    dejar,
    exportar_favoritas,
    exportar_historial,
    favoritas,
    grafico,
    guardar,
    historial,
    price,
    recibir_api_key,
    seguir,
    start,
)

load_dotenv()

seguimiento_task: asyncio.Task[None] | None = None
type App = Application[Any, Any, Any, Any, Any, Any]


def prueba_telegram_bot() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if TOKEN is None:
        raise RuntimeError("❌ Falta la variable TELEGRAM_BOT_TOKEN en el entorno.")

    # Se ejecuta justo después de iniciar el bot
    async def post_init(app: App) -> None:
        global seguimiento_task
        seguimiento_task = asyncio.create_task(comprobar_alertas_periodicamente(app))

    # Se ejecuta justo antes de cerrar el bot
    async def post_shutdown(app: App) -> None:
        global seguimiento_task
        if seguimiento_task:
            seguimiento_task.cancel()
            try:
                await seguimiento_task
            except asyncio.CancelledError:
                print("🛑 Tarea de seguimiento detenida correctamente.")

    app = Application.builder().token(TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

    # Handler conversacional para el flujo de la API Key
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PEDIR_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_api_key)],
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


def main() -> None:
    prueba_telegram_bot()


if __name__ == "__main__":
    main()
