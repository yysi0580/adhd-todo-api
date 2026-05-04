from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from app.models import AiUsageLog


class AiUsageLogRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def create(
        self,
        user_id: int | None,
        feature_name: str,
        model: str,
        prompt_version: str,
        input_tokens: int = 0,
        cached_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        estimated_cost: float = 0.0,
        cache_hit: bool = False,
        actual_openai_call: bool = False,
        source: str = "ai",
        success: bool = True,
        fallback_used: bool = False,
        error_code: str | None = None,
    ) -> AiUsageLog:
        item = AiUsageLog(
            user_id=user_id,
            feature_name=feature_name,
            model=model,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            cached_tokens=cached_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            cache_hit=cache_hit,
            actual_openai_call=actual_openai_call,
            source=source,
            success=success,
            fallback_used=fallback_used,
            error_code=error_code,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def count_since(self, since: datetime, user_id: int | None = None) -> int:
        query = self.db.query(func.count(AiUsageLog.id)).filter(AiUsageLog.created_at >= since)
        if user_id is not None:
            query = query.filter(AiUsageLog.user_id == user_id)
        return int(query.scalar() or 0)

    def count_actual_openai_calls_since(self, since: datetime, user_id: int | None = None) -> int:
        query = self.db.query(func.count(AiUsageLog.id)).filter(
            AiUsageLog.created_at >= since,
            AiUsageLog.actual_openai_call.is_(True),
        )
        if user_id is not None:
            query = query.filter(AiUsageLog.user_id == user_id)
        return int(query.scalar() or 0)

    def user_actual_openai_calls_since(self, since: datetime, user_id: int) -> int:
        return self.count_actual_openai_calls_since(since, user_id=user_id)

    def cost_since(self, since: datetime, user_id: int | None = None) -> float:
        query = self.db.query(func.coalesce(func.sum(AiUsageLog.estimated_cost), 0.0)).filter(
            AiUsageLog.created_at >= since
        )
        if user_id is not None:
            query = query.filter(AiUsageLog.user_id == user_id)
        return float(query.scalar() or 0.0)

    def cache_hits_since(self, since: datetime, user_id: int) -> int:
        return int(
            self.db.query(func.count(AiUsageLog.id))
            .filter(
                AiUsageLog.user_id == user_id,
                AiUsageLog.created_at >= since,
                AiUsageLog.cache_hit.is_(True),
            )
            .scalar()
            or 0
        )

    def fallback_count_since(self, since: datetime, user_id: int) -> int:
        return int(
            self.db.query(func.count(AiUsageLog.id))
            .filter(
                AiUsageLog.user_id == user_id,
                AiUsageLog.created_at >= since,
                AiUsageLog.fallback_used.is_(True),
            )
            .scalar()
            or 0
        )

    def fallback_reasons_since(self, since: datetime, user_id: int) -> dict[str, int]:
        rows = (
            self.db.query(AiUsageLog.error_code, func.count(AiUsageLog.id))
            .filter(
                AiUsageLog.user_id == user_id,
                AiUsageLog.created_at >= since,
                AiUsageLog.fallback_used.is_(True),
                AiUsageLog.error_code.isnot(None),
            )
            .group_by(AiUsageLog.error_code)
            .all()
        )
        return {str(error_code): int(count) for error_code, count in rows if error_code}

    def last_used_at(self, user_id: int) -> datetime | None:
        return (
            self.db.query(func.max(AiUsageLog.created_at))
            .filter(AiUsageLog.user_id == user_id)
            .scalar()
        )
