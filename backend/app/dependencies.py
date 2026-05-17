"""
Centralized dependency injection factories for FastAPI.

All service instances are created here and injected into routers via Depends().
Using @lru_cache ensures that stateless services are created once (singleton pattern)
but in a controlled, testable way — not as module-level side effects.
"""
import os
from functools import lru_cache

from fastapi import Depends, HTTPException, Request
from supabase import Client, create_client

from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.services.html_test_converter_service import HtmlConvertingService
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.services.html_cleaner_service import HtmlCleanerService
from backend.app.services.credit_service import CreditService

from backend.app.services.html_cleaner_service import HtmlCleanerService


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
def get_html_cleaner_service() -> HtmlCleanerService:
    return HtmlCleanerService()


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
        html_cleaner_service=get_html_cleaner_service()
    )

def get_current_user_id(request: Request) -> str:
    """
    Extract user ID (UUID) from the Supabase JWT token in the Authorization header.
    Uses supabase.auth.get_user() for server-side token verification.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1]

    try:
        supabase_client: Client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_KEY")
        )
        user_response = supabase_client.auth.get_user(token)
        user_id = user_response.user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")


@lru_cache
def get_credit_service() -> CreditService:
    return CreditService()
