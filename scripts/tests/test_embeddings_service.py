from backend.app.services.embeddings_service import EmbeddingsService as embedding_service

service = embedding_service()
print(service.embed_text("Hello, how are you?"))

print(len(service.embed_text("Hello, how are you?")[0]))