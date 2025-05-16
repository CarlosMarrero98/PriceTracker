import pytest
from bot import price_checker

def test_get_help_text():
    texto = price_checker.get_help_text()
    assert "/start" in texto
    assert "/price" in texto
    assert "/alerta" in texto
    assert "📋" in texto
    assert isinstance(texto, str)

def test_validate_ticker_valido(monkeypatch):
    monkeypatch.setattr("bot.price_checker.fetch_stock_price", lambda ticker: {"price": 123.45, "name": "Empresa X"})
    assert price_checker.validate_ticker("AAPL") == True

def test_validate_ticker_invalido(monkeypatch):
    monkeypatch.setattr("bot.price_checker.fetch_stock_price", lambda ticker: None)
    assert price_checker.validate_ticker("ZZZZ") == False

def test_get_alert_message_valido(monkeypatch):
    monkeypatch.setattr("bot.price_checker.fetch_stock_price", lambda ticker: {"price": 120.0, "name": "Tesla"})
    msg = price_checker.get_alert_message("TSLA")
    assert "Tesla" in msg
    assert "120.0" in msg

def test_get_alert_message_invalido(monkeypatch):
    monkeypatch.setattr("bot.price_checker.fetch_stock_price", lambda ticker: None)
    msg = price_checker.get_alert_message("XXXX")
    assert "❌" in msg
    assert "no válido" in msg
