from bot.get_price import fetch_stock_price

def validate_ticker(ticker):
    data = fetch_stock_price(ticker)
    return data is not None

def get_alert_message(ticker):
    data = fetch_stock_price(ticker)
    if not data:
        return f"❌ Ticker {ticker} no válido o no encontrado."
    return f"📊 {data['name']} ({ticker}): {data['price']} €"

def get_help_text():
    return (
        "📋 *Comandos disponibles:*\n"
        "/start - Iniciar el bot\n"
        "/login - Iniciar sesión\n"
        "/logout - Cerrar sesión\n"
        "/price <TICKER> - Ver precio de una acción\n"
        "/acciones - Ver acciones populares\n"
        "/historial <TICKER> - Ver historial de precios\n"
        "/grafico <TICKER> - Ver gráfico de la acción\n"
        "/alerta <TICKER> <MINUTOS> <MIN> <MAX> - Configurar alerta\n"
        "/seguir <TICKER> - Seguir una acción\n"
        "/dejar <TICKER> - Dejar de seguir una acción\n"
        "/favoritas - Ver tus acciones favoritas\n"
        "/portfolio - Ver tu portafolio (en desarrollo)\n"
        "/comandos - Ver comandos disponibles\n"
        "/ayuda - Ayuda rápida"
    )

