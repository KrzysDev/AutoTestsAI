from qdrant_client import QdrantClient, models
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
import json
from dotenv import load_dotenv, find_dotenv

from backend.app.services.ai_service import AiService

load_dotenv(find_dotenv())

ai_service = AiService()

client = QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# -----------------------
# FETCH
# -----------------------
points, _ = client.scroll(
    collection_name="Grammar Collection",
    scroll_filter=Filter(
        must=[
            FieldCondition(
                key="language",
                match=MatchValue(value="German")
            )
        ]
    ),
    with_payload=True,
    with_vectors=False,  # OK — nie potrzebujemy vectorów
    limit=100
)

# -----------------------
# TRANSFORM + AI
# -----------------------
def transform_payload(old):
    base_payload = {
        "id": old.get("id"),
        "language": "de",
        "subject": old.get("metadata", {}).get("subject"),
        "type": old.get("content", {}).get("type", "grammar_definition"),

        "content": {
            "definition": old.get("content", {}).get("instruction")
                or old.get("content", {}).get("body", ""),

            "structure": None,
            "signal_words": None,
            "examples": None,
            "common_mistakes": None
        }
    }

    prompt = f"""
Uzupełnij brakujące pola (None) w tym JSON.
Zwróć WYŁĄCZNIE poprawny JSON bez markdown.

JSON:
{json.dumps(base_payload, ensure_ascii=False)}
"""

    response = ai_service.ask_local(prompt)

    try:
        return json.loads(response)
    except:
        print("⚠️ AI zwróciło niepoprawny JSON — fallback")
        return base_payload

# -----------------------
# BUILD NEW DATA
# -----------------------
print("generating......")

new_payloads = {}

for i, p in enumerate(points):
    print(f"{i+1}/{len(points)}...")
    new_payloads[p.id] = transform_payload(p.payload)

# -----------------------
# UPDATE QDRANT (CLEAN REPLACE)
# -----------------------
print("updating...")

for p in points:
    # 1. usuń stary payload
    client.clear_payload(
        collection_name="Grammar Collection",
        points_selector=models.PointIdsList(
            points=[p.id]
        )
    )

    # 2. ustaw nowy payload
    client.set_payload(
        collection_name="Grammar Collection",
        points=[p.id],
        payload=new_payloads[p.id]
    )

print(f"Zaktualizowano {len(points)} punktów.")