import json
import os
import uuid
import hashlib
from qdrant_client import QdrantClient
from qdrant_client import models
from backend.app.services.ai_service import AiService
from backend.app.services.embeddings_service import EmbeddingsService
from dotenv import load_dotenv

load_dotenv()

def main():
    client = QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    embedding_service = EmbeddingsService()
    collection_name = "Language Collection"

    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_path, '..', '..'))
    file_path = os.path.join(project_root, 'data', 'extracted_tasks', 'matura_chunks_extracted.json')

    if not os.path.exists(file_path):
        print(f"Error: File not found {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Starting import of {len(data)} tasks to Qdrant...")

    for i, item in enumerate(data):
        string_id = item.get("id", f"missing-id-{i}")
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, string_id))

        try:
            text_to_embed = f"{item['content'].get('instruction', '')}\n{item['content'].get('exercise_content', '')}"
            vector = embedding_service.embed_text(text_to_embed)

            client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        payload=item,
                        vector=vector
                    )
                ]
            )
            print(f"[{i+1}/{len(data)}] Success: {string_id} -> UUID: {point_id}")
            
        except Exception as e:
            print(f"[{i+1}/{len(data)}] Error with task {string_id}: {e}")

    print("\nImport completed!")

if __name__ == "__main__":
    main()