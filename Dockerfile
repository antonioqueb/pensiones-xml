# Usar una imagen base oficial de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los requerimientos y la aplicación al contenedor
COPY requirements.txt .
COPY app.py .
COPY static/ static/
COPY templates/ templates/  # Asegúrate de incluir esta línea

# Instalar Flask
RUN pip install -r requirements.txt

# Exponer el puerto donde se ejecutará la aplicación
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
