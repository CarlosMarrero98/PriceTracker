# bot/telegram_bot.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message: str) -> bool:
    """
    Envía un mensaje de texto al chat de Telegram configurado.

    Args:
        message (str): El mensaje a enviar.

    Returns:
        bool: True si el mensaje se envió correctamente, False en caso contrario.
    """
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no están definidos en el entorno")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error al enviar mensaje: {e}")
        return False
