from backend.app.services.json_test_converting_service import JsonTestConvertingService
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import GeneratedTest, PDFTest
from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts
from backend.app.dependencies import get_ai_service, get_json_test_converting_service
import io

router = APIRouter()

@router.post("/v1/rag/test/convert", response_class=StreamingResponse)
async def convert_test(
    test_data: GeneratedTest,
    ai_service: AiService = Depends(get_ai_service),
    json_test_converting_service: JsonTestConvertingService = Depends(get_json_test_converting_service),
):
    system_prompts = SystemPrompts()
    # Use the new structured prompt
    prompt = system_prompts.get_test_restructuring_prompt(test_data)
    try:
        ai_response_raw = ai_service.ask(prompt)
        # Use the public cleaner from SystemPrompts
        ai_response = system_prompts.clean_json_response(ai_response_raw)
        test_to_convert = PDFTest.model_validate_json(ai_response)
    except Exception as e:
        print(f"Error during AI PDF structuring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to structure test for PDF generation: {e}")
    
    pdf_content = json_test_converting_service.convert_to_pdf(test_to_convert)

    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=test.pdf",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
