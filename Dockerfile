# Usa una imagen oficial de Python (ajusta la versión si usas otra)
FROM python:3.11-slim

# Crea el directorio de trabajo en el contenedor
WORKDIR /app

# Copia TODO el proyecto al contenedor
COPY . /app

# Instala pip actualizado y las dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando por defecto para ejecutar tu bot principal
CMD ["python", "main.py"]
