import io
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from backend.app.services.ai_service import AiService
from backend.app.services.html_test_converter_service import HtmlConvertingService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import FixingRequest
from backend.app.dependencies import get_ai_service, get_html_converting_service

logger = logging.getLogger(__name__)
router = APIRouter()
prompts = SystemPrompts()

@router.post("/v1/rag/test/fix")
def fix_test_html(
    request: FixingRequest,
    ai_service: AiService = Depends(get_ai_service),
    html_converting_service: HtmlConvertingService = Depends(get_html_converting_service),
):
    """
    Fixes an existing HTML test based on teacher feedback and returns the result as a PDF.
    """
    try:
        # 1. Generate the fixing prompt
        fixing_prompt = prompts.get_fixing_prompt(request.html, request.feedback)
        
        # 2. Ask AI to fix the HTML
        fixed_html = ai_service.ask(fixing_prompt, "gpt-5-mini")
        
        if not fixed_html:
            logger.error("AI returned empty string for fixed HTML")
            raise HTTPException(status_code=500, detail="AI failed to generate fixed HTML")

        # 3. Convert fixed HTML to PDF
        pdf_bytes = html_converting_service.convert_html_to_pdf(fixed_html)
        
        if not pdf_bytes:
            logger.error("HTML to PDF conversion returned no bytes after fixing")
            raise HTTPException(status_code=500, detail="Failed to convert fixed HTML to PDF")

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=fixed_test.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in fix_test_html: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
