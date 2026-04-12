from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.models.schemas import TestGeneratorRequest
import json
import io

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

@router.post("/v1/rag/test/generate-pdf", response_class=StreamingResponse)
def generate_test_pdf(request: TestGeneratorRequest):
    try:
        # 1. Generate the raw test JSON
        json_output = test_generator_service.generate_test(
            prompt=request.prompt,
            level=request.level,
            age_group=request.age_group,
            total_amount=request.total_amount
        )
        
        # 2. Convert to beautified PDF
        pdf_bytes = test_generator_service.generate_beautified_test(json_output)
        
        # 3. Return as a stream
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=english_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))