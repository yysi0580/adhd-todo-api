from datetime import datetime

from pydantic import BaseModel


class AIStatusResponse(BaseModel):
    enabled: bool
    model: str
    structuredOutput: bool
    cacheEnabled: bool
    rateLimitEnabled: bool
    budgetLimitEnabled: bool
    fallback: str
    promptVersion: str


class AIUsageMeResponse(BaseModel):
    todayCalls: int
    todayEstimatedCost: float
    monthlyEstimatedCost: float
    cacheHits: int
    fallbackCount: int
    fallbackReasons: dict[str, int]
    lastUsedAt: datetime | None
