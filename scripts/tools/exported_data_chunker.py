import tkinter as tk
from tkinter import filedialog
import json
import hashlib
from backend.app.services.chunking_service import ChunkingService as chunking_service
from backend.app.models.schemas import Chunk

def main():
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Select file",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    #making new file

    file_name = input("Enter file name: ")

    chunked_data = []
    service = chunking_service()

    for item in data:
        print(item)
        item["id"] = hashlib.md5(item["metadata"]["content"].encode()).hexdigest()[:8]
        chunk_obj = Chunk(
            id=item["id"],
            section=item["section"],
            language=item["language"],
            level=item["level"],
            metadata=item["metadata"]
        )
        new_chunks = service.chuk_vocabulary(chunk_obj, 30)
        chunked_data.extend([c.model_dump() for c in new_chunks])
    

    with open(rf"C:\Users\USER\Desktop\moje rzeczy\projekty\inne\TestGenerator\data\v1\{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(chunked_data, f, ensure_ascii=False, indent=4)

    print(data)

if __name__ == "__main__":
    main()