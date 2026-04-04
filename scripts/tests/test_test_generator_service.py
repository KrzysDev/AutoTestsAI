from backend.app.services.test_generator_service import TestGeneratorService

service = TestGeneratorService()

print(service.generate_test("en", "B2", "Jakie testy potrafisz wygenerować?", 1))