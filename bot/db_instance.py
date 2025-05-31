"""
Módulo: db_instance.py

Este módulo define una instancia global (singleton) del gestor de base de datos `DatabaseManager`.
Se utiliza para compartir una única conexión lógica a la base de datos en todo el proyecto.

Debe importarse siempre que se necesite acceder a la base de datos.
"""

from bot.db_manager import DatabaseManager

# Singleton de la base de datos
db = DatabaseManager()
