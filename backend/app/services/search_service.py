from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
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
        

def search(self, subject: str):
    result = self.client.scroll(
        collection_name="Grammar Collection",
        limit=100,
        with_payload=True,
        with_vectors=False,
        filter={
            "must": [
                {
                    "key": "subject",
                    "match": {
                        "value": subject
                    }
                }
            ]
        }
    )

    points, _ = result
    return [point.payload for point in points]
       


        
