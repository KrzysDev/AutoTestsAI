from fastapi import APIRouter, HTTPException, Request, Body, Depends
from backend.app.services.search_service import SearchService
from backend.app.dependencies import get_search_service

router = APIRouter()

@router.post("/v1/rag/search")
def search(
    text: str,
    search_service: SearchService = Depends(get_search_service),
):
    return search_service.search(text)
