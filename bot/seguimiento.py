from collections import defaultdict

SEGUIDAS = defaultdict(set)

def seguir_accion(user_id, ticker):
    SEGUIDAS[user_id].add(ticker.upper())

def dejar_de_seguir(user_id, ticker):
    SEGUIDAS[user_id].discard(ticker.upper())

def obtener_favoritas(user_id):
    return list(SEGUIDAS[user_id])
