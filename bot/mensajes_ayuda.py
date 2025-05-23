def get_commands_text() -> str:
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
        "/borrar_historial <TICKER> - Borrar historial\n"
        "/dejar <TICKER> - Dejar de seguir\n"
        "/grafico <TICKER> - Gráfico del historial\n"
        "/exportar_historial - Exportar todo tu historial\n"
        "/exportar_historial <TICKER> - Exportar historial de una acción\n"
        "/exportar_favoritas - Exportar tus favoritas\n"
    )


def get_help_text() -> str:
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
