FROM python:3.11-slim

WORKDIR /app

# 1. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

# 2. Instalar Poetry
RUN pip install poetry

# 3. Copy de dependencias para cachear instalación
COPY pyproject.toml poetry.lock* /app/

# 4. Instalar dependencias Python
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-ansi

# 5. Copiar **todo** el código de la app (ahora incluye manage.py)
COPY . /app/

# 6. Ejecutar collectstatic
RUN python manage.py collectstatic --noinput

# 7. Exponer puerto y entrypoint
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
