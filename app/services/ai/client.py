from openai import OpenAI

from app.services.ai.prompts import AI_SUGGESTION_SYSTEM_PROMPT
from app.services.ai.schemas import SuggestionResponse


class OpenAIResponsesClient:
    def __init__(self, api_key: str, model: str, timeout: float = 20.0):
        self.model = model
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def create_suggestions(self, user_input: str) -> SuggestionResponse:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": AI_SUGGESTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            text_format=SuggestionResponse,
        )
        return response.output_parsed
