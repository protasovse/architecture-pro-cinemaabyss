from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки сервиса.

    Args:
        KAFKA_BOOTSTRAP_SERVERS: брокеры Kafka, строка вида "host:port[,host2:port]"
        KAFKA_TOPIC_MOVIES: топик для событий фильмов
        KAFKA_TOPIC_USERS: топик для событий пользователей
        KAFKA_TOPIC_PAYMENTS: топик для событий платежей
    """

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC_MOVIES: str
    KAFKA_TOPIC_USERS: str
    KAFKA_TOPIC_PAYMENTS: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
