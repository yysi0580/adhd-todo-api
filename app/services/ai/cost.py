from dataclasses import dataclass


@dataclass(frozen=True)
class AIUsage:
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


def estimate_cost(
    usage: AIUsage,
    input_price_per_1m: float,
    cached_input_price_per_1m: float,
    output_price_per_1m: float,
) -> float:
    """Estimate cost from token usage.

    OpenAI prices can change. Keep prices in environment settings and confirm
    current pricing before production deploy.
    """
    normal_input_tokens = max(usage.input_tokens - usage.cached_tokens, 0)
    return (
        normal_input_tokens * input_price_per_1m / 1_000_000
        + usage.cached_tokens * cached_input_price_per_1m / 1_000_000
        + usage.output_tokens * output_price_per_1m / 1_000_000
    )
