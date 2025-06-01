"""
Módulo: mensajes_ayuda.py

Contiene funciones que devuelven textos de ayuda y comandos para el bot de Telegram.

Estos textos se utilizan en los comandos `/ayuda` y `/comandos` del bot.
"""

def get_commands_text() -> str:
    """
    Devuelve un texto con todos los comandos disponibles del bot.

    Returns:
        str: Lista formateada en Markdown de comandos de usuario.
    """
    return (
        "*Comandos disponibles:*\n"
        "/start - Iniciar el bot\n"
        "/comandos - Ver esta lista de comandos\n"
        "/ayuda - Ayuda detallada\n"
        "/seguir <TICKER> - Seguir una acción\n"
        "/favoritas - Ver tus acciones seguidas\n"
        "/price <TICKER> - Precio actual\n"
        "/historial <TICKER> - Ver historial\n"
        "/guardar <TICKER> - Guardar precio actual\n"
        "/borrar\\_historial <TICKER> - Borrar historial\n"
        "/dejar <TICKER> - Dejar de seguir\n"
        "/grafico <TICKER> - Gráfico del historial\n"
        "/exportar\\_historial - Exportar todo tu historial\n"
        "/exportar\\_historial <TICKER> - Exportar historial de una acción\n"
        "/exportar\\_favoritas - Exportar tus favoritas\n"
        "/media <TICKER> - Media del historial de precios\n"
    )


def get_help_text() -> str:
    """
    Devuelve el mensaje de ayuda detallada para nuevos usuarios.

    Returns:
        str: Mensaje explicativo con ejemplos de uso del bot.
    """
    return (
        "ℹ️ *¿Cómo funciona el bot?*\n\n"
        "1️⃣ Usa `/start` para comenzar y registrar tu usuario.\n"
        "2️⃣ El bot te pedirá tu API Key de TwelveData (puedes conseguirla gratis en https://twelvedata.com/)\n"
        "3️⃣ Empieza a seguir acciones con el comando:\n"
        "`/seguir <TICKER> [MIN] [LIM_INF] [LIM_SUP]`\n"
        "Por ejemplo: `/seguir AAPL 5 140 180`\n"
        "— Esto sigue a Apple (AAPL), revisando cada 5 minutos y avisando si el precio está fuera del rango 140$ - 180$.\n\n"
        "🔎 Consulta el precio: `/price AAPL`\n"
        "⭐ Consulta tus favoritas: `/favoritas`\n"
        "📜 Consulta el historial: `/historial AAPL`\n"
        "🗑️ Borra historial: `/borrar_historial AAPL`\n"
        "🛑 Deja de seguir: `/dejar AAPL`\n"
        "📈 Gráfico de precios: `/grafico AAPL`\n"
        "📤 Exportar historial: `/exportar_historial`\n\n"
        "Si tienes dudas, vuelve a escribir `/ayuda` o pregunta al soporte.\n"
        "¡Buena suerte con tus inversiones! 🚀\n\n"
    )
