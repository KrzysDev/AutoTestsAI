from fastapi import APIRouter, HTTPException
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.models.schemas import TestGeneratorRequest
import json

router = APIRouter()

test_generator_service = TestGeneratorService()

@router.post("/v1/rag/test/generate")
def generate_test(request: TestGeneratorRequest):
    try:
        json_output = test_generator_service.generate_test(
            prompt=request.prompt,
            level=request.level,
            age_group=request.age_group,
            total_amount=request.total_amount
        )
        return json.loads(json_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))