from bot.alerts import registrar_alerta, ALERTAS

def test_registrar_alerta():
    user_id = 1
    ticker = "AAPL"
    intervalo = 60
    registrar_alerta(user_id, ticker, intervalo)
    assert (user_id, ticker) in ALERTAS
    assert ALERTAS[(user_id, ticker)] == intervalo
