from backend.app.services.ai_service import AiService

service = AiService()

print(service.ask_cloud_with_photo("powiedz co widzisz na obrazku", "C:\\Users\\USER\\Desktop\\tapeta.png"))