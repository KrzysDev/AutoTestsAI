from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchText
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

client = QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.create_payload_index(
    collection_name="Language Data v2",
    field_name="section",
    field_schema="keyword"
)

records, next_offset = client.scroll(
    collection_name="Language Data v2",
    scroll_filter=Filter(
        must=[
            FieldCondition(
                key="section",
                match=MatchValue(value="grammar")
            )
        ]
    ),
    limit=100,
    with_payload=True,
    with_vectors=False
)

for record in records:
    print(record.payload)