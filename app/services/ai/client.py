from dataclasses import dataclass

from openai import APIConnectionError, APIStatusError, APITimeoutError, AuthenticationError, OpenAI

from app.services.ai.cost import AIUsage
from app.services.ai.exceptions import (
    AIConfigMissingError,
    AIInvalidResponseError,
    AIServiceError,
    AITimeoutError,
)
from app.services.ai.prompts import AI_SUGGESTION_SYSTEM_PROMPT
from app.services.ai.schemas import AISuggestionResponse


@dataclass(frozen=True)
class AIClientResult:
    response: AISuggestionResponse
    model: str
    usage: AIUsage


class OpenAIResponsesClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = 30.0,
        max_output_tokens: int = 700,
    ):
        if not api_key:
            raise AIConfigMissingError(
                "OpenAI API key가 설정되어 있지 않습니다.",
                code="AI_CONFIG_MISSING",
            )
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def create_suggestions(self, user_input: str) -> AIClientResult:
        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": AI_SUGGESTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
                text_format=AISuggestionResponse,
                max_output_tokens=self.max_output_tokens,
            )
        except APITimeoutError as exc:
            raise AITimeoutError(
                "AI 응답 시간이 초과되었습니다.",
                code="AI_TIMEOUT",
            ) from exc
        except AuthenticationError as exc:
            raise AIConfigMissingError(
                "OpenAI 인증 설정을 확인할 수 없습니다.",
                code="AI_CONFIG_MISSING",
            ) from exc
        except (APIConnectionError, APIStatusError) as exc:
            raise AIServiceError(
                "AI 응답을 생성하지 못했습니다. 잠시 후 다시 시도해주세요.",
                code="AI_SERVICE_ERROR",
            ) from exc
        if response.output_parsed is None:
            raise AIInvalidResponseError(
                "OpenAI structured output을 파싱하지 못했습니다.",
                code="AI_INVALID_RESPONSE",
            )
        return AIClientResult(
            response=response.output_parsed,
            model=getattr(response, "model", self.model) or self.model,
            usage=_extract_usage(response),
        )


def _extract_usage(response) -> AIUsage:
    usage = getattr(response, "usage", None)
    if usage is None:
        return AIUsage()

    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", 0) or 0
    input_details = getattr(usage, "input_tokens_details", None)
    cached_tokens = getattr(input_details, "cached_tokens", 0) if input_details else 0
    return AIUsage(
        input_tokens=input_tokens,
        cached_tokens=cached_tokens or 0,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )
