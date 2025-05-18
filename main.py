from bot.db_manager import DatabaseManager
from bot.get_price import fetch_stock_price
from bot.telegram_bot import start, comandos, ayuda, seguir, favoritas, price, guardar, historial
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

import os

load_dotenv()


def prueba_base_datos():
    # Instanciar la base de datos
    db = DatabaseManager("basedatos_test.db")  # Usamos un nombre distinto para pruebas

    # Añadir un usuario
    db.agregar_usuario("123456", "carlos_user")

    # Añadir productos seguidos por el usuario
    db.agregar_producto(
        "123456", "AAPL", "Apple Inc.", intervalo=30, limite_inf=10.0, limite_sup=200.0
    )
    db.agregar_producto(
        "123456", "TSLA", "Tesla Inc.", intervalo=15, limite_inf=500.0, limite_sup=800.0
    )

    # Guardar precios de esos productos
    db.guardar_precio("123456", "AAPL", 175.5)
    db.guardar_precio("123456", "AAPL", 180.2)
    db.guardar_precio("123456", "TSLA", 650.0)

    # Obtener productos seguidos por el usuario
    productos = db.obtener_productos("123456")
    print("Productos seguidos por el usuario:")
    for producto in productos:
        print(producto)

    # Obtener historial de precios de un producto
    historial = db.obtener_historial("123456", "AAPL")
    print("\nHistorial de precios de AAPL:")
    for entrada in historial:
        print(entrada)

    # obtener estadisticas de un producto
    estadisticas = db.obtener_estadisticas("123456", "AAPL")
    print("\nEstadísticas de AAPL:")
    for entrada in estadisticas:
        print(entrada)

    # Obtener limites de un producto
    limites = db.obtener_limites("123456", "AAPL")
    print("\nLimites de AAPL:")
    for entrada in limites:
        print(entrada)

    # Eliminar la base de datos al final
    if os.path.exists("basedatos_test.db"):
        os.remove("basedatos_test.db")
        print("\nBase de datos eliminada.")
    else:
        print("\nNo se encontró la base de datos para eliminar.")


def prueba_get_price():
    load_dotenv()  # Carga variables del archivo .env

    api_key = os.getenv("TWELVE_API_KEY")
    if not api_key:
        print("No se encontró la clave de API en el archivo .env")
        return

    simbolos = ["AAPL", "INVALIDO", "TSLA", "GOOGL", "MSFT"]

    for symbol in simbolos:
        print(f"Consultando: {symbol}")
        resultado = fetch_stock_price(symbol, api_key)

        if resultado["error"]:
            if "symbol" in resultado["error"].lower():
                print(f"Error: Símbolo inválido '{symbol}'")
            else:
                print(f"Error: {resultado['error']}")
        else:
            print(f"  ✅ {resultado['nombre']} - Precio: {resultado['precio']}")

        print()

def prueba_telegram_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("comandos", comandos))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("seguir", seguir))
    app.add_handler(CommandHandler("favoritas", favoritas))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("guardar", guardar))
    app.add_handler(CommandHandler("historial", historial))
    # Si tienes alerta, inclúyela también
    print("✅ Bot iniciado.")
    app.run_polling()


def main():
    prueba_telegram_bot()


if __name__ == "__main__":
    main()
