def get_commands_text() -> str:
    return (
        "📋 *Comandos disponibles:*\n\n"
        "/start - Inicia el bot y te registra automáticamente\n"
        "/price <TICKER> - Consulta el precio actual de una acción (ej: /price AAPL)\n"
        "/historial <TICKER> - Muestra los últimos precios registrados\n"
        "/grafico <TICKER> - Envía un gráfico de la evolución del precio\n"
        "/seguir <TICKER> - Empieza a seguir una acción para futuras alertas\n"
        "/dejar <TICKER> - Deja de seguir una acción\n"
        "/favoritas - Lista de todas las acciones que estás siguiendo\n"
        "/comandos - Muestra todos los comandos\n"
        "/ayuda - Explicación completa de cómo usar el bot"
    )


def get_help_text() -> str:
    return (
        "📖 *Guía de uso del bot:*\n\n"
        "Este bot te ayuda a seguir acciones financieras y recibir alertas de precio.\n\n"
        "👉 Empieza con /start para registrarte.\n"
        "👉 Usa /seguir <TICKER> para empezar a seguir una acción.\n"
        "👉 Configura alertas con /alerta <TICKER> <MINUTOS> <MIN> <MAX>\n\n"
        "✅ Puedes consultar precios con /price y ver historial con /historial o /grafico.\n\n"
        "🛠️ Todos los comandos disponibles están listados en /comandos.\n"
    )
