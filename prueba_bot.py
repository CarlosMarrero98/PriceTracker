import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
print(f"💡 TOKEN ACTUAL: {token}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Comando /start recibido.")
    if update.message:
        await update.message.reply_text(
            "👋 ¡Hola! El bot está funcionando correctamente."
        )


def main():
    print(token)
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot iniciado.")
    app.run_polling()


if __name__ == "__main__":
    main()
