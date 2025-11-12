FROM python:3.13.1-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="$PATH:/root/.local/bin"

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --only main --no-root --no-interaction --no-ansi --no-cache

# Копируем исходники
COPY app /app/app

EXPOSE 8082

# Запуск сервера
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--log-level", "info"]