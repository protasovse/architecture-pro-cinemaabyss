import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from .events.schemas import MovieEvent, UserEvent, PaymentEvent, ProduceResult
from .settings import settings
from .kafka import KafkaProducer
import uuid


logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Жизненный цикл приложения:
    - создаём KafkaProducer на старте
    - останавливаем его на shutdown
    """
    producer = KafkaProducer(settings.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    app_.state.producer = producer
    try:
        yield
    finally:
        await app_.state.producer.stop()


app = FastAPI(
    title="Events Service",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,  # или JSONResponse, если не ставишь orjson
    lifespan=lifespan,
)


@app.get("/api/events/health")
async def health() -> dict[str, bool]:
    """Проверка работоспособности микросервиса событий."""
    return {"status": True}


async def _publish(request: Request, topic: str, payload: dict) -> ProduceResult:
    """
    Публикует событие в Kafka и возвращает метаданные.
    Args:
        request: Request — чтобы получить producer из app.state
        topic: имя Kafka-топика
        payload: сериализуемый словарь события
    """
    producer = request.app.state.producer
    logger.info(f"------\nОтправляем в топик: {topic}, payload: {payload}")
    partition, offset = await producer.send(topic, payload)
    result = ProduceResult(partition=partition, offset=offset, event=payload)
    logger.info(f"Результат: {result.model_dump_json()}\n------")
    return ProduceResult(partition=partition, offset=offset, event=payload)


@app.post("/api/events/movie", response_model=ProduceResult, status_code=201)
async def create_movie_event(request: Request, event: MovieEvent) -> ProduceResult:
    """Создаёт событие фильма и публикует его в Kafka."""
    payload = event.model_dump()
    if not payload.get("id"):
        payload["id"] = f"movie-{payload['movie_id']}-{uuid.uuid4().hex[:8]}"
    return await _publish(request, settings.KAFKA_TOPIC_MOVIES, payload)


@app.post("/api/events/user", response_model=ProduceResult, status_code=201)
async def create_user_event(request: Request, event: UserEvent) -> ProduceResult:
    """Создаёт событие пользователя и публикует его в Kafka."""
    payload = event.model_dump()
    if not payload.get("id"):
        payload["id"] = f"user-{payload['user_id']}-{uuid.uuid4().hex[:8]}"
    return await _publish(request, settings.KAFKA_TOPIC_USERS, payload)


@app.post("/api/events/payment", response_model=ProduceResult, status_code=201)
async def create_payment_event(request: Request, event: PaymentEvent) -> ProduceResult:
    """Создаёт событие платежа и публикует его в Kafka."""
    payload = event.model_dump()
    if not payload.get("id"):
        payload["id"] = f"payment-{payload['payment_id']}-{uuid.uuid4().hex[:8]}"
    return await _publish(request, settings.KAFKA_TOPIC_PAYMENTS, payload)
