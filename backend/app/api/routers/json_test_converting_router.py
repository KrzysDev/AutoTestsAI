from backend.app.services.json_test_converting_service import JsonTestConvertingService
from fastapi import APIRouter, Response  # Dodaj Response
from backend.app.models.schemas import GeneratedTest

router = APIRouter()

json_test_converting_service = JsonTestConvertingService()

@router.post("/v1/rag/test/convert")
def convert_test(test_data: GeneratedTest):
    pdf_content = json_test_converting_service.convert_to_pdf(test_data)
    return Response(
        content=bytes(pdf_content), 
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=test.pdf"}
    )
