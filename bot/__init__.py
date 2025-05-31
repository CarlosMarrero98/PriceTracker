"""
Paquete: bot

Este paquete contiene toda la lógica principal del proyecto PriceTracker.

Módulos incluidos:
- `db_manager`: Acceso y gestión de la base de datos SQLite.
- `get_price`: Consulta de precios mediante la API de TwelveData.
- `seguimiento`: Lógica de comprobación periódica y envío de alertas.
- `telegram_bot`: Comandos y flujo de interacción con usuarios en Telegram.
- `grafico`: Generación de gráficos de evolución de precios.
- `mensajes_ayuda`: Textos reutilizables para comandos /ayuda y /comandos.
- `db_instance`: Singleton para acceso global a la base de datos.

El paquete está diseñado para funcionar con python-telegram-bot y bases de datos locales en SQLite.
"""
