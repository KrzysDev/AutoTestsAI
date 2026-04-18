from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.services.test_fixer_service import TestFixerService
from backend.app.models.schemas import TestGeneratorRequest, TestFixRequest, TestSurveyRequest
import json
import io

router = APIRouter()

test_generator_service = TestGeneratorService()
test_fixer_service = TestFixerService()

@router.post("/v1/rag/test/fix")
def fix_test(request: TestFixRequest):
    try:
        fixed_test = test_fixer_service.fix_test(
            test=request.generated_test,
            teacher_prompt=request.teacher_prompt
        )
        return fixed_test
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/v1/rag/test/generate/by_prompt")
def generate_with_prompt(request: str):
    try:
        response = test_generator_service.generate_test_from_prompt(
            prompt=request
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/rag/test/generate/by_survey")
def generate_with_survey(request: TestSurveyRequest):
    try:
        response = test_generator_service.generate_test_from_survey(
            form=request.form
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/v1/rag/test/generate_html/by_prompt")
def generate_html_test_with_prompt(request: str):
    try:
        response = test_generator_service.generate_html_test_from_prompt(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/rag/test/generate_html/by_survey")
def generate_html_test_with_survey(request: TestSurveyRequest):
    try:
        response = test_generator_service.generate_html_test_from_survey(request.form)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
