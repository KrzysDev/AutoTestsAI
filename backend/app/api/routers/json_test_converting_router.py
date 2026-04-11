from backend.app.services.json_test_converting_service import JsonTestConvertingService
from fastapi import APIRouter, Response  
from backend.app.models.schemas import GeneratedTest

from backend.app.services.ai_service import AiService
from backend.app.models.schemas import PDFTest, PDFExercise 
from backend.app.models.prompts import SystemPrompts
from fastapi import HTTPException
router = APIRouter()
ai_service = AiService()

json_test_converting_service = JsonTestConvertingService()

@router.post("/v1/rag/test/convert")
def convert_test(test_data: GeneratedTest):
    system_prompts = SystemPrompts()
    prompt = system_prompts.get_pdf_structure_prompt(test_data)
    
    try:
        ai_response = ai_service.ask(prompt)
        test_to_convert = PDFTest.model_validate_json(ai_response)
    except Exception as e:
        print(f"Error during AI PDF structuring: {e}")
        # Log AI response for debugging if needed
        print(f"AI Response was: {ai_response if 'ai_response' in locals() else 'N/A'}")
        raise HTTPException(status_code=500, detail="Failed to structure test for PDF generation.")
    
    pdf_content = json_test_converting_service.convert_to_pdf(test_to_convert)

    return Response(
        content=bytes(pdf_content), 
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=test.pdf"}
    )
