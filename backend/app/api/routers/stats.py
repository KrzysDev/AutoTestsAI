from fastapi import APIRouter
from backend.app.config.language_configs import (
    get_supported_languages,
    get_language_config,
    get_possible_language_codes
)

router = APIRouter(prefix="/v1/stats", tags=["stats"])

@router.get("/languages")
def get_language_statistics():
    """
    Returns statistics and configuration data for all supported languages.
    """
    languages = get_supported_languages()
    detailed_configs = {lang: get_language_config(lang) for lang in languages}
    
    return {
        "total_supported_languages": len(languages),
        "supported_languages": languages,
        "language_codes": get_possible_language_codes(),
        "detailed_configs": detailed_configs
    }
