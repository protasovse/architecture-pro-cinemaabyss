from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Any


class ProduceResult(BaseModel):
    """Результат публикации в Kafka."""

    status: Literal["success"] = "success"
    partition: int
    offset: int
    event: dict[str, Any]


def _get_dt():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class Event(BaseModel):
    """Базовая модель события.

    Args:
        id: уникальный идентификатор события (можно не передавать, генерируется на стороне сервиса)
        type: тип события (movie|user|payment)
        timestamp: время события в ISO 8601 (UTC)
    """

    id: str | None = None
    type: Literal["movie", "user", "payment"]
    happened_at: str = Field(default_factory=_get_dt)


class MovieEvent(Event):
    """Событие по фильму."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["movie"] = "movie"
    movie_id: int = Field(
        description="Идентификатор фильма",
        examples=[1],
    )
    title: str = Field(
        description="Название фильма",
        examples=["Inception"],
    )
    action: Literal["viewed", "rated", "added"] = "viewed"
    user_id: int | None = Field(
        default=None,
        description="Идентификатор пользователя",
    )


class UserEvent(Event):
    """Событие по пользователю."""

    type: Literal["user"] = "user"
    user_id: int
    username: str
    action: Literal["registered", "logged_in"]


class PaymentEvent(Event):
    """Событие по платежу."""

    type: Literal["payment"] = "payment"
    payment_id: int
    user_id: int
    amount: float
    status: Literal["completed", "failed"]
    timestamp: str
    method_type: str | None = None
