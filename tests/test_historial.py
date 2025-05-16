from bot.historial import guardar_precio, obtener_historial

def test_historial():
    ticker = "TEST"
    for i in range(12):
        guardar_precio(ticker, i)
    historial = obtener_historial(ticker)
    assert len(historial) <= 10
    assert historial[-1] == 11
