from pydantic_settings import BaseSettings
from pydantic import Field


def _raise():
    raise ValueError("Invalid settings")


class Settings(BaseSettings):
    """Настройки сервиса.

    Args:
        KAFKA_BOOTSTRAP_SERVERS: брокеры Kafka, строка вида "host:port[,host2:port]"
        KAFKA_TOPIC_MOVIES: топик для событий фильмов
        KAFKA_TOPIC_USERS: топик для событий пользователей
        KAFKA_TOPIC_PAYMENTS: топик для событий платежей
    """

    KAFKA_BOOTSTRAP_SERVERS: str = Field(default_factory=_raise)
    KAFKA_TOPIC_MOVIES: str = Field(default_factory=_raise)
    KAFKA_TOPIC_USERS: str = Field(default_factory=_raise)
    KAFKA_TOPIC_PAYMENTS: str = Field(default_factory=_raise)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
