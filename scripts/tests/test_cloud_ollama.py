from backend.app.services.ai_service import AiService

def main():
    service = AiService()
    answer = service.ask_ollama_cloud("czy moje zapytanie dziala?")
    print(answer)

if __name__ == "__main__":
    main()