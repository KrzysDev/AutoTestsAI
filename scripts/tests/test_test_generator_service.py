from backend.app.services.test_generator_service import TestGeneratorService

service = TestGeneratorService()

print(service.generate_test("en", "B2", "Wygeneruj test z gramatyki na temat czasu przeszłego dla uczniów na poziomie B2."))