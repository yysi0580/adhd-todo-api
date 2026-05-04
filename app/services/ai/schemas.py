from typing import Literal

from pydantic import BaseModel


class SuggestionCandidate(BaseModel):
    title: str
    micro_step: str
    effort_level: Literal["quiet", "gentle", "neutral"]
    reason: str


class SuggestionResponse(BaseModel):
    suggestions: list[SuggestionCandidate]
