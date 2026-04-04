from fastapi import APIRouter, HTTPException, Request
import ollama
from app.services.ai_service import AiService
from datetime import datetime
from collections import defaultdict

router = APIRouter()

ai_service = AiService()

last_requests_cloud = defaultdict(lambda: datetime.min)

@router.post("/v1/rag/ask/local")
def ask_ollama_local(text: str):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    try:
        return ai_service.ask_ollama_local(text)
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Ollama error: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected local model error.")

@router.post("/v1/rag/ask/cloud")
def ask_ollama_cloud(text: str, request: Request):
    client_ip = request.client.host
    now = datetime.now()
    delta = (now - last_requests_cloud[client_ip]).total_seconds()
    
    if delta < 3:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a moment.")
    
    last_requests_cloud[client_ip] = now

    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    try:
        return ai_service.ask_ollama_cloud(text, model='gpt-oss:120b')
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Ollama error: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")