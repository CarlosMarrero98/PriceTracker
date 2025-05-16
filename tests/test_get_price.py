from bot.get_price import fetch_stock_price

def test_fetch_stock_price_valido():
    result = fetch_stock_price("AAPL")
    assert result is not None
    assert "price" in result
    assert "name" in result

def test_fetch_stock_price_invalido():
    result = fetch_stock_price("INVALIDO123")
    assert result is None
