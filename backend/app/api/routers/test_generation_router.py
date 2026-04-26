import io
import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.models.languages.schemas import (
    TestSurveyRequest,
    PromptRequest,
    HtmlRequest,
)
from backend.app.services.html_test_converter_service import HtmlConvertingService
from backend.app.dependencies import (
    get_test_generator_service,
    get_html_converting_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1/rag/test/convert/html")
def convert_html_to_pdf(
    request: HtmlRequest,
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
):
    html_content = "\n".join(request.html)
    pdf_bytes = html_converting_service.convert_html_to_pdf(html_content)

    if not pdf_bytes:
        logger.error("HTML to PDF conversion returned no bytes")
        raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=generated.pdf"},
    )


@router.post("/v1/rag/test/generate_html/by_prompt")
def generate_html_test_with_prompt(
    request: PromptRequest,
    test_generator_service: TestGeneratorService = Depends(get_test_generator_service),
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
):
    try:
        result = test_generator_service.generate_html_test_from_prompt(request.prompt)

        pdf_bytes = html_converting_service.convert_html_to_pdf(result.response)
        if not pdf_bytes:
            logger.error("HTML to PDF conversion returned no bytes (by_prompt)")
            raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=generated_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise  # nie łap własnych HTTPException
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in generate_html_test_with_prompt: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/v1/rag/test/generate_html/by_survey")
def generate_html_test_with_survey(
    request: TestSurveyRequest,
    test_generator_service: TestGeneratorService = Depends(get_test_generator_service),
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
):
    try:
        result = test_generator_service.generate_html_test_from_survey(request.form)

        pdf_bytes = html_converting_service.convert_html_to_pdf(result.response)
        if not pdf_bytes:
            logger.error("HTML to PDF conversion returned no bytes (by_survey)")
            raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=generated_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in generate_html_test_with_survey: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")