from fastapi import APIRouter
from backend.app.services.test_generator_service import TestGeneratorService
from typing import Literal

router = APIRouter()

test_generator_service = TestGeneratorService()

@router.post("/v1/rag/test/generate")
def generate_test(topic: str):
    return test_generator_service.generate_test(topic)