from fastapi import APIRouter, HTTPException
import ollama
from app.services.ai_service import AiService

router = APIRouter()

ai_service = AiService()

@router.post("/v1/rag/ask/local")
def ask_local(text: str):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Tekst wejściowy nie może być pusty")
    try:
        return ai_service.ask_local(text)
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Błąd Ollama: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Nieoczekiwany blad modelu lokalnego.")

@router.post("/v1/rag/ask/cloud")
def ask_cloud(text: str):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Tekst wejściowy nie może być pusty")
    try:
        return ai_service.ask_cloud(text)
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Błąd Ollama: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Wystąpił nieoczekiwany błąd serwera.")