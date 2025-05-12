# tests/test_telegram_bot.py

import os
import pytest
from bot.telegram_bot import send_telegram_message


@pytest.mark.skipif(
    not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"),
    reason="Variables de entorno TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no definidas"
)
def test_send_telegram_message_returns_true():
    success = send_telegram_message("Mensaje de prueba desde test_telegram_bot ✅")
    assert success
