from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Filter
import os
from dotenv import load_dotenv

import math

load_dotenv()

# <summary>
# Service used to connect to Qdrant cluster and fetch vector embeddings or points based on subjects.
# </summary>
class SearchService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.client.create_payload_index(
            collection_name="Grammar Collection",
            field_name="subject",
            field_schema="keyword"
        )
        

    def search(self, subject: str, collection: str = "Grammar Collection", language: str = None):
        # Build filter conditions dynamically
        must_conditions = [
            {
                "key": "subject",
                "match": {
                    "value": subject
                }
            }
        ]

        # Optionally filter by language (e.g. "de", "en", "fr")
        if language:
            must_conditions.append(
                {
                    "key": "language",
                    "match": {
                        "value": language
                    }
                }
            )

        result = self.client.scroll(
            collection_name=collection,
            limit=100,
            with_payload=True,
            with_vectors=False,
            scroll_filter={"must": must_conditions}
        )

        points, _ = result
        return [p.payload for p in points]


        
