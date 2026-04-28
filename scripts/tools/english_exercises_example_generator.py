import os
import json
import uuid
import sys
import re
from typing import List, Dict, Any, Union

# Add the project root to sys.path to allow imports from backend
# This script is in scripts/tools/, so root is ../../
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.services.search_service import SearchService
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

class LocalAiService:
    def __init__(self, model="qwen3-coder:30b"):
        # The user mentioned qwen3-coder:30b specifically
        self.client = Client(host="http://localhost:11434")
        self.model = model

    def ask(self, prompt: str) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Error calling local AI: {e}")
            return ""

def clean_json(text: str) -> str:
    """Extracts JSON content from a string that might contain markdown fences."""
    # Find ```json ... ``` or ``` ... ```
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        return json_match.group(1).strip()
    
    # If no fences, try to find the first { or [ and last } or ]
    start_idx = text.find('{')
    if start_idx == -1:
        start_idx = text.find('[')
    
    end_idx = text.rfind('}')
    if end_idx == -1:
        end_idx = text.rfind(']')
        
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1].strip()
        
    return text.strip()

def generate_exercises():
    search_service = SearchService()
    ai_service = LocalAiService()
    
    # English subjects from Qdrant
    subjects_en = [
        "Present Simple", "Present Continuous", "Present Perfect", "Present Perfect Continuous",
        "Past Simple", "Past Continuous", "Past Perfect", "Past Perfect Continuous",
        "Future Simple", "Going to", "Future Continuous", "Future Perfect", "Future Perfect Continuous"
    ]
    
    # German subjects (standard ones as fallback/base)
    subjects_de = [
        "Präsens", "Präteritum", "Perfekt", "Plusquamperfekt", "Futur I", "Futur II"
    ]
    
    tasks = [
        {"lang": "en", "subjects": subjects_en},
        {"lang": "de", "subjects": subjects_de}
    ]
    
    for task in tasks:
        lang = task["lang"]
        subjects = task["subjects"]
        all_exercises = []
        
        print(f"\n=== Generating exercises for {lang.upper()} ===", flush=True)
        
        for subject in subjects:
            print(f"\nProcessing {subject}...", flush=True)
            
            # 1. Retrieval
            retrieval_data = search_service.search(subject)
            context = json.dumps(retrieval_data, indent=2) if retrieval_data else "No specific grammar data found in RAG."
            
            # 2. Generate initial 5 items
            gen_prompt = f"""
            You are an expert language teacher (Specializing in {lang.upper()}). 
            Generate exactly 5 grammar exercise items for the subject: {subject}.
            
            Grammar Context (RAG):
            {context}
            
            Each item should be a sentence with a gap or a transformation. 
            Provide the result ONLY as a JSON object with this structure:
            {{
                "instruction": "Instruction for the task (e.g., 'Put the verb in brackets into the correct form.')",
                "items": [
                    {{
                        "body": "Sentence with gap, e.g., 'I (go) to school.'",
                        "answer": "go"
                    }},
                    ...
                ]
            }}
            Return ONLY valid JSON. No explanations.
            """
            
            raw_response = ai_service.ask(gen_prompt)
            cleaned_json_str = clean_json(raw_response)
            
            try:
                gen_data = json.loads(cleaned_json_str)
                instruction = gen_data.get("instruction", "Complete the task.")
                items = gen_data.get("items", [])
                
                for item in items:
                    # 3. Generate paraphrases for each item
                    print(f"  Generating paraphrases for: {item['body']}", flush=True)
                    
                    para_prompt = f"""
                    You are a language teacher. Given the following grammar exercise item for {subject} in {lang.upper()}:
                    Body: {item['body']}
                    Answer: {item['answer']}
                    
                    Grammar Context (RAG):
                    {context}
                    
                    Generate 3 paraphrases (variations) of this item. Each paraphrase should test the SAME grammatical point ({subject}) but using different vocabulary or context.
                    Return ONLY a JSON list of 3 objects:
                    [
                        {{ "body": "...", "answer": "..." }},
                        {{ "body": "...", "answer": "..." }},
                        {{ "body": "...", "answer": "..." }}
                    ]
                    Return ONLY valid JSON.
                    """
                    
                    raw_para = ai_service.ask(para_prompt)
                    para_json_str = clean_json(raw_para)
                    
                    try:
                        paraphrases = json.loads(para_json_str)
                        variants = [item] + paraphrases
                        
                        for variant in variants:
                            exercise_entry = {
                                "id": str(uuid.uuid4()),
                                "metadata": {
                                    "subject": subject,
                                    "topic": "Grammar",
                                    "difficulty": "Intermediate",
                                    "age_group": "adults"
                                },
                                "content": {
                                    "type": "gap_fill",
                                    "instruction": instruction,
                                    "body": variant["body"],
                                    "answer_key": variant["answer"]
                                }
                            }
                            all_exercises.append(exercise_entry)
                            
                    except Exception as e:
                        print(f"    Error parsing paraphrases for {subject}: {e}", flush=True)
                        exercise_entry = {
                            "id": str(uuid.uuid4()),
                            "metadata": {
                                "subject": subject,
                                "topic": "Grammar",
                                "difficulty": "Intermediate",
                                "age_group": "adults"
                            },
                            "content": {
                                "type": "gap_fill",
                                "instruction": instruction,
                                "body": item["body"],
                                "answer_key": item["answer"]
                            }
                        }
                        all_exercises.append(exercise_entry)
                
                # Incremental save after each subject
                output_file = f"example_exercises_{lang}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(all_exercises, f, indent=2, ensure_ascii=False)
                print(f"  Successfully saved progress for {subject} to {output_file}", flush=True)
                        
            except Exception as e:
                print(f"  Error parsing initial items for {subject}: {e}", flush=True)

        print(f"\nSuccessfully saved {len(all_exercises)} exercises to {output_file}", flush=True)

if __name__ == "__main__":
    generate_exercises()
