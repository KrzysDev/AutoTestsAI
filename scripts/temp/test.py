from backend.app.models.schemas import GeneratedTest
import json
print(GeneratedTest.model_json_schema())