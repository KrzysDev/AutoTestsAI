from backend.app.services.ai_service import AiService

service = AiService()

def main():
    print(service.ask_cloud_with_photo("describe what you see in the image", "C:\\Users\\USER\\Desktop\\tapeta.png"))

if __name__ == "__main__":
    main()