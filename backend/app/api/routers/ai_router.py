from fastapi import APIRouter, HTTPException, Request, Body
import ollama
from backend.app.services.ai_service import AiService
from datetime import datetime
from collections import defaultdict

router = APIRouter()

ai_service = AiService()

last_requests_cloud = defaultdict(lambda: datetime.min)

@router.post("/v1/rag/ask")
async def ask_ollama_cloud(request: Request, text: str = Body(..., description="Query for the cloud AI")):
    client_ip = request.client.host
    now = datetime.now()
    delta = (now - last_requests_cloud[client_ip]).total_seconds()
    
    if delta < 3:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a moment.")
    
    last_requests_cloud[client_ip] = now

    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    try:
        return ai_service.ask(text)
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Ollama error: {e.error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred. Error: {e}")