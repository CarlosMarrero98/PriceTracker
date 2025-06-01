# Usa una imagen oficial y ligera de Python
FROM python:3.12-slim

# Instala pip y Poetry
RUN pip install --upgrade pip && pip install poetry

# Crea el directorio de trabajo en el contenedor
WORKDIR /app

# Copia SOLO los archivos de dependencias primero (mejora la caché)
COPY pyproject.toml poetry.lock* /app/

# Instala las dependencias SIN crear entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copia el resto del proyecto
COPY . /app

# Comando por defecto para ejecutar el bot
CMD ["python", "main.py"]
