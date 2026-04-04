import json
from qdrant_client import QdrantClient, models
from backend.app.services.ai_service import AiService
import hashlib

def substring_between(text, start, end):
    i = text.find(start)
    if i == -1:
        return None
    i += len(start)
    j = text.find(end, i)
    if j == -1:
        return None
    return text[i:j]


def main():

    ai_service = AiService()

    all_responses = []

    with open(r"C:\Users\USER\Desktop\moje rzeczy\projekty\inne\TestGenerator\data\extracted_tasks\matura_chunks.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for filename, file_data in data.items():
        tasks = file_data["tasks"]

        for counter, exercise in enumerate(tasks):
            # Pomijamy pierwszy element (instrukcja/strona tytułowa)
            if counter == 0:
                continue

            next_task_marker = f"Zadanie {counter + 1}" if counter < len(tasks) - 1 else "\n"
            this_exercise_text = substring_between(exercise, f"Zadanie {counter}", next_task_marker)

            # Jeśli substring_between nie znalazł — użyj całego tekstu zadania
            if this_exercise_text is None:
                this_exercise_text = exercise

            exercise_id = hashlib.md5(this_exercise_text.encode("utf-8")).hexdigest()[:8]

            prompt = f"""Jesteś ekspertem od testów z języka angielskiego.
            Twoim zadaniem jest wyciagniecie danych z zadania w takim formacie
            
            {{
                "id": "exercise-{exercise_id}",
                "language": "eng/de",
                "subject": "np. Present Simple / Present Perfect / Past Simple / Multiple Choice itp.",
                "type": "vocabulary/grammar/listening/reading",
                "content": {{
                    "instruction": "polecenie",
                    "exercise_content": "treść zadania"
                }}
            }}

            ##WYTYCZNE
            - Absolutnie NIC NIE MOZE znalezc sie w twojej odpowiedzi poza czystym jsonem. Nie poprzedzaj go znakami takimi jak ```json lub nie koncz takimi jak ```
            - pozostaw pole ID takie jakie juz zostalo ci podane
            - uzupelniaj pola zgodnie z komentarzami obok
            - pole moze miec tylko jedna opcje. Nie mieszaj jezykow
            - nie mieszaj takze subject, nie lacz zadnych pol, kazde pole POZA polami w content musi byc jednym slowem

            ##ZADANIE
            {this_exercise_text}
            """

            response = ai_service.ask_ollama_local(prompt, 'gemma4:latest')
            print(f"[{filename}] Zadanie {counter}:\n{response}\n")

            try:
                json_response = json.loads(response)
            except:
                print(f"Error parsing JSON for exercise {counter} in file {filename}")
                continue

            all_responses.append(json_response)



    with open(r"C:\Users\USER\Desktop\moje rzeczy\projekty\inne\TestGenerator\data\extracted_tasks\matura_chunks_extracted.json", "w", encoding="utf-8") as f:
        json.dump(all_responses, f, indent=4, ensure_ascii=False)
            



if __name__ == "__main__":
    main()