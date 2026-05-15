import io
import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from backend.app.services.test_generator_service import TestGeneratorService

from backend.app.models.schemas import (
    PromptRequest,
    HtmlRequest,
    TestSurveyRequest,
    TestGeneratorHTMLResponse,
)
from backend.app.services.html_test_converter_service import HtmlConvertingService
from backend.app.dependencies import (
    get_test_generator_service,
    get_html_converting_service,
    get_credit_service,
)
from backend.app.services.credit_service import CreditService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1/rag/test/convert/html")
async def convert_html_to_pdf(
    request: HtmlRequest,
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
):
    from fastapi.concurrency import run_in_threadpool
    html_content = request.html
    pdf_bytes = await run_in_threadpool(html_converting_service.convert_html_to_pdf, html_content)

    if not pdf_bytes:
        logger.error("HTML to PDF conversion returned no bytes")
        raise HTTPException(status_code=500, detail="Failed to convert HTML to PDF")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=generated.pdf"},
    )


class TooManyCharactersError(Exception):
    pass


@router.post("/v1/rag/test/generate_html/by_prompt")
async def generate_html_test_with_prompt(
    request: PromptRequest,
    test_generator_service: TestGeneratorService = Depends(get_test_generator_service),
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
    credit_service: CreditService = Depends(get_credit_service),
):
    print("Request received: generate_html_test_with_prompt")
    if len(request.prompt) > 10000:
        raise TooManyCharactersError()
        return None
    try:
        print("deducting credit....")
        credit_service.deduct_credit(request.email)
        print("generating test....")
        result = await test_generator_service.generate_html_test_from_prompt(request.prompt)
        return result
    except HTTPException:
        raise 
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in generate_html_test_with_prompt: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")




@router.post("/v1/rag/test/generate_html/by_survey")
async def generate_html_test_with_survey(
    request: TestSurveyRequest,
    test_generator_service: TestGeneratorService = Depends(get_test_generator_service),
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
    credit_service: CreditService = Depends(get_credit_service),
):
    logger.info("Request received: generate_html_test_with_survey")
    try:
        credit_service.deduct_credit(request.email)
        result = await test_generator_service.generate_html_test_from_survey(request.form)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in generate_html_test_with_survey: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")