FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd

# Instalar poetry
RUN pip install poetry

# Copiar sólo los archivos de dependencias primero
COPY pyproject.toml poetry.lock* /app/

# Instalar dependencias del proyecto
RUN poetry config virtualenvs.create false && poetry install --no-root
RUN python manage.py collectstatic --noinput


# Ahora sí, copiar todo el código
COPY . /app/

# Exponer puerto
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]