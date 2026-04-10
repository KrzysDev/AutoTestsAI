import os
import json
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load env variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def download_grammar():
    client = QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    offset = None
    grammar_chunks = []

    grammar_subjects = {
        'Present Simple', 'Present Continuous', 'Present Perfect', 
        'Present Perfect Continuous', 'Past Simple', 'Past Continuous', 
        'Past Perfect', 'Past Perfect Continuous', 'Future Simple (will)', 
        'Going to', 'Future Continuous', 'Future Perfect', 'Future Perfect Continuous'
    }

    while True:
        batch, next_offset = client.scroll(
            collection_name="Grammar Collection",
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False, 
        )

        for point in batch:
            subject = point.payload.get("subject")
            if subject in grammar_subjects:
                grammar_chunks.append(point.payload)

        if next_offset is None:
            break
        offset = next_offset

    # Determine saving path
    target_dir = os.path.join(os.path.dirname(__file__), '../../backend/app/models/json_schemas')
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, 'grammar_definitions_chunks.json')

    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(grammar_chunks, f, ensure_ascii=False, indent=4)

    print(f"Downloaded {len(grammar_chunks)} grammar definitions and saved to {target_file}")

if __name__ == "__main__":
    download_grammar()
