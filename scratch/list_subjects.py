from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

records, _ = client.scroll(
    collection_name="Grammar Collection",
    limit=100,
    with_payload=True,
    with_vectors=False
)

subjects = set()
for r in records:
    subjects.add(r.payload.get("subject"))

print("Subjects in Qdrant:")
for s in sorted(list(subjects)):
    print(f"- {s}")
