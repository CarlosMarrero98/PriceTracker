# PriceTracker

Aplicación para monitorizar el precio de productos (como zapatillas) en una tienda online. El sistema detecta cambios de precio y envía notificaciones por Telegram. También guarda un historial de precios para cada producto y calcula estadísticas como el precio mínimo, máximo y promedio.

---

## Tecnologías utilizadas

- Python 3.10+
- [Poetry](https://python-poetry.org/) (gestión de entorno y dependencias)
- SQLite (base de datos local)
- Requests (para consultar precios)
- Pytest (para testing)
- GitHub Actions (para integración continua)

---

## Instalación del entorno

1. Instala Poetry (si no lo tienes):

    ```bash
    pip install poetry
    ```

2. Clona el repositorio:

    ```bash
    git clone git@github.com:TU_USUARIO/PriceTracker.git
    cd PriceTracker
    ```

3. Instala las dependencias del proyecto:

    ```bash
    poetry install
    ```

4. Activa el entorno virtual:

    ```bash
    poetry shell
    ```

---

## Estado del proyecto

Actualmente en desarrollo. Se ha configurado:

- Entorno con Poetry
- Integración continua con GitHub Actions
- Test básico de prueba funcionando

---

## Tests

Actualmente existe un test de prueba para comprobar que el entorno CI funciona correctamente.

Para ejecutarlos localmente:

```bash
poetry run pytest
```

---

## Integración continua

El proyecto está configurado para ejecutar pruebas automáticamente en GitHub Actions cada vez que se realiza un push o un pull request. Puedes ver el estado de las acciones en la pestaña "Actions" del repositorio.

---
