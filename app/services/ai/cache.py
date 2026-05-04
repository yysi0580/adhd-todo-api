import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.time import utc_now
from app.services.ai.schemas import AISuggestionResponse


@dataclass
class AICacheEntry:
    response: AISuggestionResponse
    expires_at: datetime


class InMemoryAICache:
    """Small process-local cache. TODO: replace with Redis for multi-worker deploys."""

    def __init__(self):
        self._items: dict[str, AICacheEntry] = {}

    def get(self, key: str) -> AISuggestionResponse | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        if entry.expires_at <= utc_now():
            self._items.pop(key, None)
            return None
        return entry.response

    def set(self, key: str, response: AISuggestionResponse, ttl_minutes: int) -> None:
        self._items[key] = AICacheEntry(
            response=response,
            expires_at=utc_now() + timedelta(minutes=ttl_minutes),
        )

    def clear(self) -> None:
        self._items.clear()


def normalize_ai_input(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def hash_ai_input(value: str) -> str:
    return hashlib.sha256(normalize_ai_input(value).encode("utf-8")).hexdigest()


ai_cache = InMemoryAICache()
