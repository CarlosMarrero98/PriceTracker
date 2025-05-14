from bot.get_price import fetch_stock_price
from bot.historial import guardar_precio
import asyncio

# Estructura: (user_id, ticker) -> {intervalo, min, max}
ALERTAS = {}

async def gestionar_alertas(app):
    print("🔁 Servicio de alertas iniciado...")
    while True:
        for (user_id, ticker), config in list(ALERTAS.items()):
            print(f"\n⏱️ Comprobando {ticker} para user {user_id}...")

            data = fetch_stock_price(ticker)
            if data:
                precio = data["price"]
                guardar_precio(ticker, precio)

                print(f"💰 Precio actual de {ticker}: {precio}€ — Rango configurado: {config['min']}€ - {config['max']}€")

                # ✅ ALERTA si el precio está DENTRO del rango
                if config["min"] <= precio <= config["max"]:
                    msg = (
                        f"🔔 *Alerta de precio* para {data['name']} ({ticker}): {precio} €\n"
                        f"✅ Dentro del rango: {config['min']} € - {config['max']} €"
                    )
                    try:
                        print(f"📨 Enviando alerta a {user_id}...")
                        await app.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                        print("✅ Mensaje enviado correctamente")
                    except Exception as e:
                        print(f"❌ Error al enviar mensaje a {user_id}: {e}")
                else:
                    print("ℹ️ Precio fuera del rango, sin alerta.")

            else:
                print(f"⚠️ No se pudo obtener el precio de {ticker}")

            await asyncio.sleep(config["intervalo"])

        await asyncio.sleep(5)

def registrar_alerta(user_id, ticker, intervalo, min_price, max_price):
    ALERTAS[(user_id, ticker.upper())] = {
        "intervalo": intervalo,
        "min": min_price,
        "max": max_price
    }
    print(f"📌 Alerta registrada: {ticker} | cada {intervalo}s | rango {min_price} - {max_price} para user {user_id}")

