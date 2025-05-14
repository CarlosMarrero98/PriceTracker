from bot.get_price import fetch_stock_price
from bot.historial import guardar_precio
import asyncio

ALERTAS = {}  # (user_id, ticker): intervalo_en_segundos

async def gestionar_alertas(app):
    while True:
        for (user_id, ticker), intervalo in list(ALERTAS.items()):
            data = fetch_stock_price(ticker)
            if data:
                guardar_precio(ticker, data["price"])
                msg = f"🔔 {data['name']} ({ticker}): {data['price']} €"
                try:
                    await app.bot.send_message(chat_id=user_id, text=msg)
                except Exception as e:
                    print(f"[Error alerta usuario {user_id}]: {e}")
            await asyncio.sleep(intervalo)
        await asyncio.sleep(5)  # Evita sobrecarga si hay muchas alertas

def registrar_alerta(user_id, ticker, intervalo):
    ALERTAS[(user_id, ticker.upper())] = intervalo
