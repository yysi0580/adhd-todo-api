from app.services.suggestion import (
    RuleBasedSuggestionGenerator,
    SuggestionGenerator,
    get_suggestion_generator,
)

SuggestionService = SuggestionGenerator
RuleBasedSuggestionService = RuleBasedSuggestionGenerator
get_suggestion_service = get_suggestion_generator

__all__ = [
    "RuleBasedSuggestionGenerator",
    "RuleBasedSuggestionService",
    "SuggestionGenerator",
    "SuggestionService",
    "get_suggestion_generator",
    "get_suggestion_service",
]
