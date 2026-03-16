from fastapi import APIRouter
from app.services.ai_service import AiService

router = APIRouter()

ai_service = AiService()

@router.post("/v1/rag/ask/local")
def ask_local(text: str):
    return ai_service.ask_local(text)

@router.post("/v1/rag/ask/cloud")
def ask_cloud(text: str):
    return ai_service.ask_cloud(text)