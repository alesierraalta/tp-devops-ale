# Usa una imagen base oficial de Python Alpine
FROM python:3.9-alpine

# Establece un directorio de trabajo
WORKDIR /app

# Instala las dependencias necesarias para compilar ciertas librerías de Python
RUN apk add --no-cache gcc musl-dev

# Copia los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de tu aplicación al contenedor
COPY . .

# Define la variable de entorno para indicar a Flask cómo ejecutar la aplicación
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["flask", "run"]
