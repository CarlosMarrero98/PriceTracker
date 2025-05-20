import asyncio
from bot.db_instance import db
from bot.get_price import fetch_stock_price
from collections import defaultdict
from datetime import datetime, timedelta

"""
Módulo encargado del seguimiento automático de precios y envío de alertas por Telegram.

Lanza un bucle asincrónico que consulta los activos seguidos por cada usuario,
registra precios y envía mensajes si se superan los límites establecidos.
"""

async def lanzar_seguimiento(app):
    """
    Lanza la tarea de comprobación periódica de alertas como una tarea asincrónica del bot.

    Args:
        app: Instancia de la aplicación de Telegram creada con `Application.builder().build()`.
    """
    app.create_task(comprobar_alertas_periodicamente(app))

async def comprobar_alertas_periodicamente(app) -> None:
    """
    Bucle principal que revisa periódicamente los precios de los activos seguidos por los usuarios.

    - Para cada usuario, recupera su API Key almacenada.
    - Verifica si ha pasado suficiente tiempo según el intervalo configurado.
    - Guarda el nuevo precio en la base de datos.
    - Si el precio está fuera de los límites definidos, envía una alerta al usuario por Telegram.

    Args:
        app: Instancia de la aplicación de Telegram.
    """
    print("🔁 Iniciando seguimiento automático...")

    ultima_revision: dict[tuple[str, str], datetime] = defaultdict(lambda: datetime.min)

    while True:
        usuarios = db.obtener_usuarios()

        for chat_id in usuarios:
            api_key = db.obtener_api_key(chat_id)
            if not api_key:
                print(f"Usuario {chat_id} no tiene API Key registrada. Saltando alertas.")
                continue

            productos = db.obtener_productos(chat_id)

            for symbol, intervalo_min, nombre, limite_inf, limite_sup in productos:
                clave = (chat_id, symbol)
                ahora = datetime.now()

                if ahora - ultima_revision[clave] < timedelta(minutes=intervalo_min):
                    continue

                ultima_revision[clave] = ahora

                # Usa la API Key del usuario
                data = fetch_stock_price(symbol, api_key)

                if data["error"] or data["precio"] is None:
                    print(f"Error en {symbol}: {data['error']}")
                    continue

                precio_actual = data["precio"]
                db.guardar_precio(chat_id, symbol, precio_actual)

                if not (limite_inf <= precio_actual <= limite_sup):
                    mensaje = (
                        f"🚨 *Alerta de precio*\n\n"
                        f"{nombre} ({symbol})\n"
                        f"💰 Precio actual: {precio_actual:.2f}$\n"
                        f"Fuera del rango: {limite_inf}$ - {limite_sup}$"
                    )
                    try:
                        await app.bot.send_message(
                            chat_id=chat_id, text=mensaje, parse_mode="Markdown"
                        )
                        print(f"✅ Alerta enviada a {chat_id}")
                    except Exception as e:
                        print(f"Error al enviar mensaje a {chat_id}: {e}")

                await asyncio.sleep(1)

        await asyncio.sleep(
            30
        )  # No hace falta dormir mucho, ya respetamos cada intervalo
