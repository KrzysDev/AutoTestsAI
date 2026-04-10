from backend.app.services.ai_service import AiService

service = AiService()

def main():
    print(service.ask_ollama_local("Zaplanuj test z gramatyki jezyka angielskiegona temat czasu przeszłego dla uczniów na poziomie B2."))

if __name__ == "__main__":
    main()