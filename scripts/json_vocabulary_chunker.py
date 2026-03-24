from backend.app.services.chunking_service import ChunkingService
import json

chunking_service = ChunkingService()


def main():
    with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\extracted_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    chunked_data = []
    i = 0

    folder_name = input("Podaj nazwę folderu: ")
    file_name = input("Podaj nazwę pliku: ")

    for chunk in data:
        if chunk['section'] == 'vocabulary':
            chunked_data.extend(chunking_service.chunk_vocabulary(chunk))
            chunk['id'] = f"vocab-{i}"
        i+=1

    
    with open(f"data/{folder_name}/{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(chunked_data, f, indent=2)

if __name__ == "__main__":
    main()