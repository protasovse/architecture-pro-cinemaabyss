# Events Service (CinemaAbyss)

Микросервис событий. Принимает HTTP-запросы и публикует события в Kafka.

## Эндпоинты
- `GET /api/events/health` — health-check
- `POST /api/events/movie` — событие фильма
- `POST /api/events/user` — событие пользователя
- `POST /api/events/payment` — событие платежа

## Конфигурация (ENV)
- `KAFKA_BOOTSTRAP_SERVERS` (по умолчанию `kafka:9092`)
- `KAFKA_TOPIC_MOVIES` (по умолчанию `events.movies`)
- `KAFKA_TOPIC_USERS` (по умолчанию `events.users`)
- `KAFKA_TOPIC_PAYMENTS` (по умолчанию `events.payments`)

## Локальный запуск
```bash
poetry install
poetry run uvicorn app.main:app --reload --port 8082
```