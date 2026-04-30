"""
Central registry of supported languages for test generation.

To add a new language:
  1. Add a new entry to LANGUAGE_CONFIGS below.
  2. Ensure the corresponding Qdrant data is uploaded (see scripts/tools/upload_grammar_data.py).
  3. No changes to services or prompts are required — they read language from the request.
"""

LANGUAGE_CONFIGS: dict[str, dict] = {
    "English": {
        "code": "en",
        # Qdrant collection used to retrieve grammar/vocabulary context
        "qdrant_collection": "Grammar Collection",
        # None means no language filter applied (whole collection is English)
        "qdrant_language_filter": None,
        "supported_task_types": ["vocabulary", "grammar", "reading", "writing"],
        "description": "English (global default)",
    },
    "German": {
        "code": "de",
        "qdrant_collection": "Grammar Collection",
        # Filter by payload field: {"key": "language", "match": {"value": "de"}}
        "qdrant_language_filter": "de",
        "supported_task_types": ["grammar", "reading", "writing"],
        "description": "German (Deutsch)",
    },
    # ── Template for a new language ────────────────────────────────────────────
    # "French": {
    #     "code": "fr",
    #     "qdrant_collection": "Grammar Collection",
    #     "qdrant_language_filter": "fr",
    #     "supported_task_types": ["vocabulary", "grammar", "reading", "writing"],
    #     "description": "French (Français)",
    # },
}


def get_language_config(language: str) -> dict:
    """
    Returns the config dict for a given language name.
    Falls back to English if the language is not registered.
    """
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])


def get_supported_languages() -> list[str]:
    """Returns a list of all registered language names."""
    return list(LANGUAGE_CONFIGS.keys())
