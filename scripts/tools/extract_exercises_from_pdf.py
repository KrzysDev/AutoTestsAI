from ollama import chat
from ollama import ChatResponse
import tkinter as tk
from tkinter import filedialog
import os
from pypdf import PdfReader
import json

from backend.app.services.ai_service import AiService

service = AiService()


def main():
    root = tk.Tk()
    root.withdraw()  

    folder_path = filedialog.askdirectory()

    print("Folder:", folder_path)

    length = len(os.listdir(folder_path))

    save_folder_path = filedialog.askdirectory()

    current = 1

    all_responses = []

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".pdf"):
            continue

        full_path = os.path.join(folder_path, file_name)
        
        reader = PdfReader(full_path)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        extracted_text = text

        prompt = f"""
                To sa zadania na poziomie B2 z matur. Przesylam ci rozne pliki maturalne. Masz z nich wyciagnac ABSOLUTNIE WSZYSTKIE WSZYSTKIE WSZYSTKIE zadania i zapisac je jako odzielne pliki json. Masz zrobic jedna wielka strukture jako liste podstruktur gdzie kazda podstruktura przechowuje zadanie. Powtrzam lista ma miec WSZYSTKIE WSZYSTKIE WSZYSTKIE zadania z tych WSZYSTKICH arkuszy.

                #Format
                [
                {{
                "level": "B1",pozostawiasz bez zmian
                "age_group": "teens", pozostawiasz bez zmian
                "task_type": "" , tu okreslasz - reading, writing, vocabulary, grammar lub listening
                "topic": "", topic w przypadku grammar jest jakims czasem gramatyki, vocabulary to temat slowek a czytanie i pisanie to tematy tego co uczen czyta badz pisze

                "content": {{
                "instruction": "...", polecenie do zadania
                "body": "...", tresc zadania wewnatrz
                "source": "matura"  pozostawiasz bez zmian
                }}
                }},
                .....
                ]

                provided text:
                {extracted_text}

                #zasady
                - mozesz zwrocic  WYLACZNIE FORMAT JSON. BRAK MARKDOWN ```json oraz ```. Musi byc koniecznie SAM CZYSTY JSON
                - nie zwracaj niz przed ani po wymaganym formacie, sam czysty format nic wiecej.


        """

        response = service.ask(prompt)

        print(response)

        count = 0

        max_tries = 5

        while(count < max_tries):
            try:
                parsed = json.loads(response)
                all_responses.extend(parsed)
                break
            except:
                print("Błąd parsowania JSON dla:", file_name)
                response: ChatResponse = chat(model='qwen2.5:14b-instruct', messages=[
                {
                    'role': 'user',
                    'content': prompt
                }])
            count += 1

        print(f"{current}/{length}")
        current += 1

    output_path = os.path.join(save_folder_path, "extracted_eng.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_responses, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()


