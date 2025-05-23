def get_commands_text() -> str:
    return (
        "📋 *Comandos disponibles:*\n\n"
        "/start — Inicia el bot y registra tu usuario\n"
        "/comandos — Muestra esta lista de comandos\n"
        "/ayuda — Explicación rápida de cómo funciona el bot\n"
        "/seguir <TICKER> [MIN] [LIM_INF] [LIM_SUP] — Empieza a seguir una acción y recibe alertas\n"
        "/favoritas — Lista de acciones que estás siguiendo\n"
        "/price <TICKER> — Consulta el precio actual de una acción\n"
        "/guardar <TICKER> — Guarda el precio actual de una acción en tu historial\n"
        "/historial <TICKER> — Ver tu historial de precios guardados\n"
        "/borrar_historial <TICKER> — Borra el historial de una acción\n"
        "/dejar <TICKER> — Deja de seguir una acción\n"
        "/grafico <TICKER> — Recibe el gráfico histórico de precios\n"
        "/exportar_favoritas — Exporta la lista de acciones que sigues y sus límites (no contiene precios)\n"
        "/exportar_historial — Exporta el historial completo de precios guardados (todas las acciones y fechas)\n"
        
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
