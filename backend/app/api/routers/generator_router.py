from fastapi import APIRouter, HTTPException
from app.services.test_generator_service import TestGeneratorService
from app.models.schemas import TestGeneratorRequest, Test

router = APIRouter(prefix="/v1/generator", tags=["generator"])
test_generator_service = TestGeneratorService()

@router.post("/generate", response_model=Test)
async def generate_test(request: TestGeneratorRequest):
    try:
        test = test_generator_service.generate_all_groups(
            language=request.language,
            level=request.level,
            topic=request.topic,
            group_count=request.group_count
        )
        return test
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
