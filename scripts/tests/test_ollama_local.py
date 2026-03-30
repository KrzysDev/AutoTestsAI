from backend.app.services.ai_service import AiService

def main():
    service = AiService()
    print(service.ask_ollama_local("Hello, how are you?"))

if __name__ == "__main__":
    main()