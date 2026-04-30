from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

import json

from dotenv import load_dotenv

load_dotenv()

import os

import qdrant_client

from backend.app.services.embeddings_service import EmbeddingsService

embeddings = EmbeddingsService()

with open("data/example_exercises_english.json", "r", encoding="utf8") as file:
    data = json.load(file)


count = 1


for exercise in data:
    # Initialize client
    client = qdrant_client.QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
    ) 
    
    print(f"uploading.... {count}/{len(data)}")

    client.upsert(
        collection_name="Example_Ex_Eng",
        points=[
            PointStruct(
                id=count, 
                vector=embeddings.embed_text(str(exercise['content'])), 
                payload=exercise
            ),
        ]
    )

    count += 1


