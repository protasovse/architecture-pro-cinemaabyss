FROM python:3.13.1-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:/root/.local/bin"
COPY pyproject.toml poetry.lock /app/
ENV POETRY_VIRTUALENVS_PATH=/usr/src/.venv \
    POETRY_VIRTUALENVS_IN_PROJECT=0
RUN poetry install --only main --no-root --no-cache

# Копируем исходники
COPY ./app/main.py /app/main.py

EXPOSE 8000

# Запуск сервера
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
