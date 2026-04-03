import os
import sys
import json
import uuid

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from backend.app.services.embeddings_service import EmbeddingsService

load_dotenv()

def import_data():
    client = QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    embeddings_service = EmbeddingsService()
    
    collection_name = "LanguageData"

    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_path, '..', '..'))

    vocab_file = os.path.join(project_root, 'data', 'v1', 'english', 'vocabulary', 'chunked_vocabulary.json')
    grammar_file = os.path.join(project_root, 'data', 'v1', 'english', 'grammar', 'extracted_grammar.json')

    files_to_process = [vocab_file, grammar_file]
    
    for file_path in files_to_process:
        if not os.path.exists(file_path):
            print(f"Pomijam {file_path} - plik nie istnieje.")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        points = []
        print(f"Przetwarzam {len(data)} chunków z {os.path.basename(file_path)}...")
        
        for i, chunk in enumerate(data):
            try:
                text_to_embed = json.dumps(chunk, ensure_ascii=False)
                vector = embeddings_service.embed_text(text_to_embed)
                
                point_id = str(uuid.uuid4())
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=chunk  
                ))
                
                if len(points) >= 50:
                    client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    points = []
                    print(f"Wrzucono punkt {i+1} / {len(data)}...")
            except Exception as e:
                print(f"Błąd podczas przetwarzania chunka (index {i}): {e}")
                
        if points:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            print(f"Wrzucono wszystkie pozostałe punkty.")
            
        print(f"Zakończono publikację paczek z {os.path.basename(file_path)}!\n")

if __name__ == "__main__":
    import_data()
