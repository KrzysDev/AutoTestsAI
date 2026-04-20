from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io
from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.services.test_fixer_service import TestFixerService
from backend.app.models.schemas import (
    TestGeneratorRequest, 
    TestFixRequest, 
    TestSurveyRequest,
    PromptRequest,
    HtmlRequest
)

from backend.app.services.html_test_converter_service import HtmlConvertingService
import json
import io

router = APIRouter()

test_generator_service = TestGeneratorService()
test_fixer_service = TestFixerService()

html_converting_service = HtmlConvertingService()

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

from fastapi import Body

@router.post("/v1/rag/test/convert/html")
def convert_html_to_pdf(request: HtmlRequest):

    request.html = "\n".join(request.html)
    pdf_bytes = html_converting_service.convert_html_to_pdf(request.html)


    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=generated.pdf"
        }
    )

@router.post("/v1/rag/test/generate/by_prompt")
def generate_with_prompt(request: PromptRequest):
    try:
        response = test_generator_service.generate_test_from_prompt(
            prompt=request.prompt
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
def generate_html_test_with_prompt(request: PromptRequest):
    try:
        result = test_generator_service.generate_html_test_from_prompt(request.prompt)
        
        pdf_bytes = html_converting_service.convert_html_to_pdf(result.response)
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=generated_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/rag/test/generate_html/by_survey")
def generate_html_test_with_survey(request: TestSurveyRequest):
    try:
        result = test_generator_service.generate_html_test_from_survey(request.form)
        
        pdf_bytes = html_converting_service.convert_html_to_pdf(result.response)
        
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=generated_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
