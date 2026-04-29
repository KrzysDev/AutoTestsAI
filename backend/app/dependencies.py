"""
Centralized dependency injection factories for FastAPI.

All service instances are created here and injected into routers via Depends().
Using @lru_cache ensures that stateless services are created once (singleton pattern)
but in a controlled, testable way — not as module-level side effects.
"""
from functools import lru_cache
from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.services.html_test_converter_service import HtmlConvertingService
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService


@lru_cache
def get_ai_service() -> AiService:
    return AiService()


@lru_cache
def get_search_service() -> SearchService:
    return SearchService()


@lru_cache
def get_html_converting_service() -> HtmlConvertingService:
    return HtmlConvertingService()





@lru_cache
def get_classification_service() -> ClassificationService:
    return ClassificationService(ai_service=get_ai_service())


@lru_cache
def get_prompt_parser_service() -> PromptParserService:
    return PromptParserService(ai_service=get_ai_service())


@lru_cache
def get_test_generator_service() -> TestGeneratorService:
    return TestGeneratorService(
        ai_service=get_ai_service(),
        search_service=get_search_service(),
        classification_service=get_classification_service(),
        prompt_parser_service=get_prompt_parser_service(),
    )



