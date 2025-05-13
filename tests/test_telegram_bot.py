import os
import pytest
from telegram.ext import Application
from unittest.mock import patch


@pytest.fixture
def telegram_token():
    return os.getenv("TELEGRAM_BOT_TOKEN")


def test_token_exists(telegram_token):
    assert telegram_token is not None
    assert telegram_token.startswith("1")  # tokens reales suelen empezar por "1"


def test_application_builds(telegram_token):
    app = Application.builder().token(telegram_token).build()
    assert isinstance(app, Application)
    assert app.bot is not None


@patch("bot.telegram_bot.Application.builder")
def test_main_builds_application(mock_builder):
    from bot import telegram_bot
    assert mock_builder.called, "Application.builder() should be called in main()"
