from collections import defaultdict, deque

HISTORIAL = defaultdict(lambda: deque(maxlen=10))

def guardar_precio(ticker, precio):
    HISTORIAL[ticker.upper()].append(precio)

def obtener_historial(ticker):
    return list(HISTORIAL[ticker.upper()])
