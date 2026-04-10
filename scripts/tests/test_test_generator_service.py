from backend.app.services.test_generator_service import TestGeneratorService

service = TestGeneratorService()

print(service.generate_all_groups("en", "B2", "Wygeneruj test ze słownictwa dotyczącego podróżowania po Anglii", 2))
