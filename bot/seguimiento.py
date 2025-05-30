"""
Módulo de seguimiento automático de precios y envío de alertas por Telegram.

Este módulo lanza una tarea asincrónica que comprueba periódicamente
los precios de acciones o activos seguidos por los usuarios registrados.
Cuando un precio supera los límites definidos, el bot envía una alerta.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from telegram.ext import Application

from bot.db_instance import db
from bot.get_price import fetch_stock_price

logging.basicConfig(level=logging.INFO)

ultima_revision: dict[tuple[str, str], datetime] = defaultdict(lambda: datetime.min)

type App = Application[Any, Any, Any, Any, Any, Any]


async def lanzar_seguimiento(app: App) -> None:
    """
    Lanza la tarea asincrónica que controla el seguimiento de precios.

    Este método se llama normalmente desde el `post_init` del bot.

    Args:
        app: Instancia de la aplicación de Telegram.
    """
    app.create_task(comprobar_alertas_periodicamente(app))


async def comprobar_alertas_periodicamente(app: App) -> None:
    """
    Tarea asincrónica que ejecuta el seguimiento de todos los usuarios cada 30 segundos.

    Itera por todos los usuarios registrados, comprueba los precios y envía
    alertas si es necesario.

    Args:
        app: Instancia de la aplicación de Telegram.
    """
    logging.info("🔁 Iniciando seguimiento automático...")
    while True:
        try:
            usuarios = db.obtener_usuarios()
            for chat_id in usuarios:
                await procesar_usuario(app, chat_id)
        except Exception as e:
            logging.error(f"Error general en el seguimiento: {e}")
        await asyncio.sleep(30)


async def procesar_usuario(app: App, chat_id: str) -> None:
    """
    Procesa todos los activos seguidos por un usuario concreto.

    Comprueba si es momento de revisar un símbolo según su intervalo,
    consulta el precio, guarda el valor y envía una alerta si es necesario.

    Args:
        app: Instancia de la aplicación de Telegram.
        chat_id (str): ID del chat del usuario.
    """
    try:
        api_key = db.obtener_api_key(chat_id)
        if not api_key:
            logging.warning(f"Usuario {chat_id} no tiene API Key registrada. Saltando alertas.")
            return

        productos = db.obtener_productos(chat_id)

        for symbol, intervalo_min, nombre, limite_inf, limite_sup in productos:
            clave = (chat_id, symbol)
            ahora = datetime.now()

            if ahora - ultima_revision[clave] < timedelta(minutes=intervalo_min):
                continue

            ultima_revision[clave] = ahora

            data = fetch_stock_price(symbol, api_key)
            if data["error"] or data["precio"] is None:
                logging.warning(f"Error en {symbol}: {data['error']}")
                continue

            precio_actual = float(data["precio"])
            db.guardar_precio(chat_id, symbol, precio_actual)

            if not (limite_inf <= precio_actual <= limite_sup):
                mensaje = (
                    f"🚨 *Alerta de precio*\n\n"
                    f"{nombre} ({symbol})\n"
                    f"💰 Precio actual: {precio_actual:.2f}$\n"
                    f"Fuera del rango: {limite_inf}$ - {limite_sup}$"
                )
                try:
                    await app.bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="Markdown")
                    logging.info(f"✅ Alerta enviada a {chat_id}")
                except Exception as e:
                    logging.error(f"Error al enviar mensaje a {chat_id}: {e}")

            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"Error al procesar usuario {chat_id}: {e}")
