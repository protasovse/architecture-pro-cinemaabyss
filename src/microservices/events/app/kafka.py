import json
from aiokafka import AIOKafkaProducer
from typing import Any


class KafkaProducer:
    """Лёгкая обёртка над AIOKafkaProducer."""

    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode(
                    "utf-8"
                ),
            )
            await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def send(self, topic: str, value: dict[str, Any]) -> tuple[int, int]:
        """Публикует сообщение и возвращает (partition, offset)."""
        assert self._producer is not None, "Producer is not started"
        md = await self._producer.send_and_wait(topic, value=value)
        return md.partition, md.offset
