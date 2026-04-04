from fastapi import APIRouter
from backend.app.services.test_generator_service import TestGeneratorService

router = APIRouter()

test_generator_service = TestGeneratorService()

@router.post("/v1/rag/test/generate")
def generate_test(language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str, group_count: int = 2):
    return test_generator_service.generate_all_groups(language, level, topic)