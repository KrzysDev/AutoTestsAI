from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
from dotenv import load_dotenv

import math

load_dotenv()

class SearchService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("CLUSTER_ENDPOINT"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        

    def search(self, subject: str):
        all_points = []
        offset = None

        while True:
            batch, next_offset = self.client.scroll(
                collection_name="Grammar Collection",
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True, 
            )

            all_points.extend(batch)

            if next_offset is None:
                break

            offset = next_offset

        filtered_points = [
            point for point in all_points
            if point.payload.get("subject").startswith(subject)
        ]
        
        return [point.payload for point in filtered_points]
       


        
