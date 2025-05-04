from bot.get_price import get_price


def test_get_price_returns_float():
    price = get_price("123")
    assert isinstance(price, float)

# Comprobar que el resultado es 99.99
def test_get_price_returns_correct_value():
    price = get_price("123")
    assert price == 99.99