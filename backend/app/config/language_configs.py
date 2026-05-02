
from qdrant_client import QdrantClient, models

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_language_subjects(language: str) -> list[str]:
    subjects = set()
    client = QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    # Inicjalizacja zmiennych do obsługi paginacji
    scroll_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="language",
                match=models.MatchValue(value=language),
            ),
        ]
    )
    
    next_offset = None
    batch_size = 100 

    while True:
        records, next_offset = client.scroll(
            collection_name="Grammar Collection",
            scroll_filter=scroll_filter,
            limit=batch_size,
            offset=next_offset,
            with_payload=True,
            with_vectors=False 
        )

        for record in records:
            if record.payload and "subject" in record.payload:
                subjects.add(record.payload["subject"])

        if next_offset is None:
            break

    return sorted(list(subjects))
    



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
        "description": "English (English)",
        "allowed_retrival_subjects" : f"{get_language_subjects("en")}"
    },
    "German": {
        "code": "de",
        "qdrant_collection": "Grammar Collection",
        # Filter by payload field: {"key": "language", "match": {"value": "de"}}
        "qdrant_language_filter": "de",
        "supported_task_types": ["grammar", "reading", "writing"],
        "description": "German (Deutsch)",
        "allowed_retrival_subjects" : f"{get_language_subjects("de")}"
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

def get_possible_language_codes() -> list[str]:
    result = []

    for lang_name, config in LANGUAGE_CONFIGS.items():
        result.append(f'{config["code"]} for {lang_name} language')

    return result

def get_language_config(language: str) -> dict:
    """
    Returns the config dict for a given language name.
    Falls back to English if the language is not registered.
    """
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["English"])


def get_supported_languages() -> list[str]:
    """Returns a list of all registered language names."""
    return list(LANGUAGE_CONFIGS.keys())

