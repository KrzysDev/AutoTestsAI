from fastapi import APIRouter, HTTPException, Request, Body
import ollama
from backend.app.services.search_service import SearchService

router = APIRouter()

search_service = SearchService()

@router.post("/v1/rag/search")
def search(text: str = Body(...), top_k: int = Body(5)):
    return search_service.search(text, top_k)
    

