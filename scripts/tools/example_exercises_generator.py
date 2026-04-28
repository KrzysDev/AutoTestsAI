import os
import json
import uuid
import sys
import re
from typing import List, Dict, Any

# Add project root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, root_path)

from backend.app.services.search_service import SearchService
from backend.app.services.embeddings_service import EmbeddingsService
from ollama import Client
from dotenv import load_dotenv
import qdrant_client
from qdrant_client import models

load_dotenv()

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1"]

class LocalAiService:
    def __init__(self, model="qwen3-coder:30b"):
        self.client = Client(host="http://localhost:11434")
        self.model = model

    def ask(self, prompt: str) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Error calling local AI: {e}", flush=True)
            return ""

def clean_json(text: str) -> str:
    if not text:
        return ""

    # extract code block JSON
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        return json_match.group(1).strip()

    # fallback brute extraction: find the VERY FIRST occurrence of { or [
    start_candidates = [i for i in [text.find('{'), text.find('[')] if i != -1]
    if not start_candidates:
        return text.strip()
    
    start_idx = min(start_candidates)
    end_idx = max(text.rfind('}'), text.rfind(']'))

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1].strip()

    return text.strip()


def safe_json_load(text: str, fallback):
    cleaned = clean_json(text)
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"DEBUG: JSON load failed. Cleaned text: {cleaned[:100]}... Error: {e}", flush=True)
        return fallback


def generate_exercises():
    search_service = SearchService()
    embeddings_service = EmbeddingsService()
    ai_service = LocalAiService()

    q_client = qdrant_client.QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = "example_exercises"

    # init collection
    try:
        q_client.get_collection(collection_name)
    except Exception:
        print(f"Creating collection: {collection_name}", flush=True)
        q_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
        )

        q_client.create_payload_index(collection_name, "metadata.subject", models.PayloadSchemaType.KEYWORD)
        q_client.create_payload_index(collection_name, "language", models.PayloadSchemaType.KEYWORD)
        q_client.create_payload_index(collection_name, "metadata.cefr", models.PayloadSchemaType.KEYWORD)

    subjects_en = [
        "Present Simple", "Present Continuous", "Present Perfect",
        "Past Simple", "Past Continuous", "Future Simple"
    ]

    subjects_de = [
        "Präsens", "Perfekt", "Präteritum", "Futur I",
        "Konjunktiv II", "Passiv", "Modalverben"
    ]

    tasks = [
        {"lang": "en", "subjects": subjects_en},
        {"lang": "de", "subjects": subjects_de}
    ]

    for task in tasks:
        lang = task["lang"]
        subjects = task["subjects"]
        all_exercises = []

        print(f"\n=== Generating exercises for {lang.upper()} ===", flush=True)

        for subject in subjects:
            print(f"\nProcessing {subject}...", flush=True)

            retrieval_data = search_service.search(subject)
            context = json.dumps(retrieval_data, indent=2) if retrieval_data else "No grammar data."

            # generate per CEFR level
            for level in CEFR_LEVELS:

                gen_prompt = f"""
You are an expert {lang.upper()} teacher.
Generate exactly 5 grammar exercises.

Topic: {subject}
CEFR Level: {level}

Rules:
- Adjust difficulty strictly to CEFR level
- A1: very simple sentences
- A2: basic structures
- B1: intermediate grammar
- B2: complex sentences
- C1: advanced / nuanced grammar

Context:
{context}

Return ONLY valid JSON:
{{
  "instruction": "Task instruction",
  "items": [
    {{"body": "...", "answer": "..."}}
  ]
}}
"""

                raw = ai_service.ask(gen_prompt)
                gen_data = safe_json_load(raw, {})

                instruction = gen_data.get("instruction", "Complete the task.")
                items = gen_data.get("items", [])
                
                print(f"    Level {level}: Generated {len(items)} items", flush=True)

                for item in items:
                    para_prompt = f"""
Create 2 paraphrases of this {lang.upper()} exercise.
CEFR level: {level}

Body: {item.get('body')}
Answer: {item.get('answer')}

Return JSON list:
[{{"body":"...","answer":"..."}}]
"""

                    raw_para = ai_service.ask(para_prompt)
                    paraphrases = safe_json_load(raw_para, [])
                    print(f"      Item paraphrases: {len(paraphrases)}", flush=True)

                    variants = [item] + paraphrases

                    for variant in variants:
                        ex_id = str(uuid.uuid4())

                        entry = {
                            "id": ex_id,
                            "language": lang,
                            "metadata": {
                                "subject": subject,
                                "cefr": level,
                                "topic": "grammar",
                                "difficulty": level
                            },
                            "content": {
                                "type": "gap_fill",
                                "instruction": instruction,
                                "body": variant.get("body", ""),
                                "answer_key": variant.get("answer", "")
                            }
                        }

                        all_exercises.append(entry)

                        vector = embeddings_service.embed_text(entry["content"]["body"])

                        q_client.upsert(
                            collection_name=collection_name,
                            points=[
                                models.PointStruct(
                                    id=ex_id,
                                    payload=entry,
                                    vector=vector
                                )
                            ]
                        )

            # save progress
            with open(f"example_exercises_{lang}.json", "w", encoding="utf-8") as f:
                json.dump(all_exercises, f, indent=2, ensure_ascii=False)

            print(f"Saved {subject} for {lang}", flush=True)

    print("Done.")


if __name__ == "__main__":
    generate_exercises()
