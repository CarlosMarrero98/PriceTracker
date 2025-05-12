# tests/test_telegram_bot.py

from bot.telegram_bot import send_telegram_message


def test_send_telegram_message_returns_true():
    success = send_telegram_message("Mensaje de prueba desde test_telegram_bot ")
    assert success
