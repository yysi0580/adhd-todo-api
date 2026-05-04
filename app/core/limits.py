from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.time import utc_now


@dataclass
class WindowCounter:
    count: int
    reset_at: datetime


_rate_limits: dict[str, WindowCounter] = {}
_login_failures: dict[str, WindowCounter] = {}
_login_blocked_until: dict[str, datetime] = {}


def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    now = utc_now()
    counter = _rate_limits.get(key)
    if counter is None or counter.reset_at <= now:
        _rate_limits[key] = WindowCounter(
            count=1,
            reset_at=now + timedelta(seconds=window_seconds),
        )
        return True

    counter.count += 1
    return counter.count <= limit


def is_login_blocked(key: str) -> bool:
    blocked_until = _login_blocked_until.get(key)
    return blocked_until is not None and blocked_until > utc_now()


def record_login_failure(key: str, limit: int, block_minutes: int) -> None:
    now = utc_now()
    counter = _login_failures.get(key)
    if counter is None or counter.reset_at <= now:
        counter = WindowCounter(count=0, reset_at=now + timedelta(minutes=block_minutes))
        _login_failures[key] = counter

    counter.count += 1
    if counter.count >= limit:
        _login_blocked_until[key] = now + timedelta(minutes=block_minutes)


def clear_login_failures(key: str) -> None:
    _login_failures.pop(key, None)
    _login_blocked_until.pop(key, None)


def reset_limits() -> None:
    _rate_limits.clear()
    _login_failures.clear()
    _login_blocked_until.clear()
