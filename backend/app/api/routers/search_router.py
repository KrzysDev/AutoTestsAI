from fastapi import APIRouter, HTTPException, Request
import ollama
from app.services.search_service import SearchService

router = APIRouter()

search_service = SearchService()

@router.post("/v1/rag/search")
def search(text: str, top_k: int = 5):
    return search_service.search(text, top_k)
    

