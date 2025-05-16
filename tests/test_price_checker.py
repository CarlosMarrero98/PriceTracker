from bot.price_checker import get_alert_message, validate_ticker

def test_validate_ticker_valido():
    assert validate_ticker("AAPL") == True

def test_validate_ticker_invalido():
    assert validate_ticker("INVALIDO123") == False

def test_get_alert_message_valido():
    msg = get_alert_message("AAPL")
    assert "AAPL" in msg or "aapl" in msg.lower()

def test_get_alert_message_invalido():
    msg = get_alert_message("INVALIDO123")
    assert "no válido" in msg.lower()
