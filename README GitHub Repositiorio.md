# PriceTracker

Aplicación para monitorizar el precio de acciones en tiempo real utilizando la API de Twelve Data. Permite consultar información financiera a través de un bot de Telegram, facilitando el seguimiento de tus activos favoritos de forma sencilla y directa.

---

## Tecnologías utilizadas

- Python 3.10+
- [Poetry](https://python-poetry.org/) (gestión de entorno y dependencias)
- SQLite (base de datos local para almacenar información relevante)
- Twelve Data API (para obtener precios de acciones)
- Telegram Bot (para interactuar con el sistema)
- Pytest (para testing)

---

## Instalación del entorno

1. Instala Poetry (si no lo tienes):

    ```bash
    pip install poetry
    ```

2. Clona el repositorio:

    ```bash
    git clone https://github.com/CarlosMarrero98/PriceTracker.git
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

## Ejecución del proyecto

Una vez dentro del entorno virtual, ejecuta el archivo principal:

```bash
python main.py
```

Asegúrate de tener configuradas correctamente las variables necesarias (como el token del bot de Telegram y la API key de Twelve Data).

---

## Tests

Los tests están ubicados en el directorio `tests/`.

Para ejecutarlos localmente con Poetry:

```bash
poetry run pytest
```

O bien, si ya estás dentro del entorno virtual:

```bash
pytest
```

---

## Estado del proyecto

Actualmente en desarrollo. Funcionalidad básica operativa con:

- Integración con Twelve Data API
- Bot de Telegram funcional para consultas
- Base de datos local con SQLite
- Sistema de tests en marcha

---

## Contribuciones

¡Toda ayuda es bienvenida! Si quieres colaborar:

1. Haz un fork del repositorio.
2. Crea una rama con tu funcionalidad o mejora.
3. Haz tus cambios y asegúrate de que todo funcione.
4. Abre un Pull Request con una descripción clara de lo que has hecho.

Si encuentras algún problema o tienes sugerencias, no dudes en abrir un [issue](https://github.com/TU_USUARIO/PriceTracker/issues).

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

---
