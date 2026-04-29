import json
import os
import hashlib
import uuid
import sys
from dotenv import load_dotenv
import qdrant_client
from qdrant_client import models

# Add project root to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, root_path)

from backend.app.services.embeddings_service import EmbeddingsService

load_dotenv()

def upload_german_grammar():
    # Path to the German grammar data file
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../german_data_.json'))
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Initialize services
    embeddings_service = EmbeddingsService()
    client = qdrant_client.QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    # Ensure language index exists for filtering
    client.create_payload_index(
        collection_name="Grammar Collection",
        field_name="language",
        field_schema="keyword"
    )

    # 1. DELETE existing German points to avoid duplicates/legacy data
    print("Deleting existing German grammar points...")
    client.delete(
        collection_name="Grammar Collection",
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="language",
                        match=models.MatchValue(value="de")
                    )
                ]
            )
        )
    )

    # 2. Load new data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    length = len(data)
    print(f"Uploading {length} updated German grammar points to Qdrant...")

    for i, item in enumerate(data):
        print(f"Processing {i+1}/{length}: {item.get('subject')}")
        
        # Use a stable UUID based on the 'id' field in the JSON
        # This is better than hashing the content which might change
        item_id = item.get('id', str(uuid.uuid4()))
        # If item_id is not a valid UUID string, we can hash it to create one
        try:
            point_id = str(uuid.UUID(item_id))
        except ValueError:
            # Hash the string ID to get a valid UUID
            hash_bytes = hashlib.sha256(item_id.encode()).digest()
            point_id = str(uuid.UUID(bytes=hash_bytes[:16]))
        
        content_str = str(item.get('content', ''))
        
        # Create embedding
        vector = embeddings_service.embed_text(content_str)
        
        # Upsert into Grammar Collection
        client.upsert(
            collection_name="Grammar Collection",
            points=[
                models.PointStruct(
                    id=point_id,
                    payload=item,
                    vector=vector
                )
            ]
        )

    print("Upload complete!")

if __name__ == "__main__":
    upload_german_grammar()
