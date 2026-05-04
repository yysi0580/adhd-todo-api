from app.core.exceptions import AppError


class AIServiceError(AppError):
    code = "AI_SERVICE_ERROR"
    status_code = 502


class AIRateLimitExceededError(AppError):
    code = "AI_RATE_LIMIT_EXCEEDED"
    status_code = 429


class AIBudgetExceededError(AppError):
    code = "AI_BUDGET_EXCEEDED"
    status_code = 429


class AIDailyLimitExceededError(AppError):
    code = "AI_DAILY_LIMIT_EXCEEDED"
    status_code = 429


class AIMonthlyBudgetExceededError(AppError):
    code = "AI_MONTHLY_BUDGET_EXCEEDED"
    status_code = 429


class AIInvalidResponseError(AppError):
    code = "AI_INVALID_RESPONSE"
    status_code = 502


class AITimeoutError(AppError):
    code = "AI_TIMEOUT"
    status_code = 504


class AIConfigMissingError(AppError):
    code = "AI_CONFIG_MISSING"
    status_code = 500
