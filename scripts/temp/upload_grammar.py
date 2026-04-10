import json
import tkinter as tk
from tkinter import filedialog
import qdrant_client
from qdrant_client import models
from dotenv import load_dotenv
from backend.app.services.embeddings_service import EmbeddingsService
import os

import hashlib
import uuid

service = EmbeddingsService()

load_dotenv()

client = qdrant_client.QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

length = len(data)
current = 0
for item in data:
    current += 1
    print(f"Processing {current}/{length}")
    hash_bytes = hashlib.sha256(str(item['content']).encode()).digest()
    id = str(uuid.UUID(bytes=hash_bytes[:16]))
    client.upsert(
        collection_name="Grammar Collection",
        points=[ 
            models.PointStruct(
                id=id,
                payload=item,
                vector=service.embed_text(str(item["content"]))
            )
        ]
    )
