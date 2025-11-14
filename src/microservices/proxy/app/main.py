import os
import random
from typing import Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse


def _parse_percent(value: Optional[str], default: int = 0) -> int:
    """Безопасный парсинг процента 0..100."""
    try:
        v = int(value)
        return max(0, min(100, v))
    except Exception:  # noqa
        return default


app = FastAPI()

PORT: int = int(os.getenv("PORT", "8000"))
MONOLITH_URL: str = os.getenv("MONOLITH_URL", "http://monolith:8080")
MOVIES_SERVICE_URL: str = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
EVENTS_SERVICE_URL: str = os.getenv("EVENTS_SERVICE_URL", "http://events-service:8082")
GRADUAL_MIGRATION: bool = os.getenv("GRADUAL_MIGRATION", "false").lower() == "true"
MOVIES_MIGRATION_PERCENT: int = _parse_percent(
    os.getenv("MOVIES_MIGRATION_PERCENT"), 50
)
API_MOVIES = "/api/movies"
API_USERS = "/api/users"
API_PAYMENTS = "/api/payments"
API_SUBSCRIPTIONS = "/api/subscriptions"

# --- Клиент для проксирования (keep-alive, таймауты) ---
client = httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0))


@app.get("/health")
async def health() -> Response:
    """Простой endpoint для liveness/readiness."""
    return PlainTextResponse("ok")


async def _proxy(request: Request, target_base: str, path: str) -> Response:
    """Проксирование запроса в целевой сервис с пробросом метода, query и тела."""
    url = httpx.URL(target_base).join(path)
    method = request.method
    # Читаем тело запроса один раз
    body = await request.body()
    # Базовые заголовки + trace-id (если есть)
    headers = dict(request.headers)
    # Удалим hop-by-hop (хоповые) заголовки
    for h in [
        "host",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    ]:
        headers.pop(h, None)

    try:
        resp = await client.request(
            method,
            url,
            content=body,
            headers=headers,
            params=request.query_params,
        )
    except httpx.ConnectError:
        return PlainTextResponse(content="404 Not found", status_code=404)

    # Возвращаем ответ как есть, включая статус и тело
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
    )


def gradual() -> bool:
    if GRADUAL_MIGRATION:
        choice = random.randint(1, 100)
        return choice <= MOVIES_MIGRATION_PERCENT
    return False


@app.get("/api/movies/health")
async def movies_health(req: Request) -> Response:
    """health check только для микросервиса"""
    return await _proxy(
        request=req, target_base=MOVIES_SERVICE_URL, path="/api/movies/health"
    )


@app.api_route(
    f"{API_MOVIES}{{full_path:path}}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def route_movies(req: Request, full_path: str = "") -> Response:
    """
    Канареечная маршрутизация:
    - Если GRADUAL_MIGRATION=true, с вероятностью MOVIES_MIGRATION_PERCENT -> Movies Service.
    - Иначе -> Monolith.
    """
    target = MONOLITH_URL if gradual() else MOVIES_SERVICE_URL

    return await _proxy(
        request=req,
        target_base=target,
        path=f"{API_MOVIES}{full_path}",
    )


@app.api_route(
    f"{API_USERS}{{full_path:path}}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def route_users(req: Request, full_path: str = "") -> Response:
    """Пользователи пока обслуживаются монолитом."""
    return await _proxy(req, MONOLITH_URL, f"{API_USERS}{full_path}")


@app.api_route(
    f"{API_PAYMENTS}{{full_path:path}}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def route_payments(req: Request, full_path: str = "") -> Response:
    """Платежи пока обслуживаются монолитом."""
    return await _proxy(req, MONOLITH_URL, f"{API_PAYMENTS}{full_path}")


@app.api_route(
    f"{API_SUBSCRIPTIONS}{{full_path:path}}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def route_subscriptions(req: Request, full_path: str = "") -> Response:
    """Платежи пока обслуживаются монолитом."""
    return await _proxy(req, MONOLITH_URL, f"{API_SUBSCRIPTIONS}{full_path}")
