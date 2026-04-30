import sys
import os
import json
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

# Add backend to path so we can import models and services
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import FormSection
from backend.app.utils.json_utils import clean_json_response

load_dotenv()

def main():
    ai_service = AiService()
    prompts = SystemPrompts()
    
    # Initialize Qdrant Client for retrieval
    qdrant_client = QdrantClient(
        url=os.getenv("CLUSTER_ENDPOINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    
    # Define tasks with their specific generator methods
    tasks = [
        {"type": "grammar_mcq", "method": prompts.get_grammar_mcq_prompt},
        {"type": "grammar_gap_fill", "method": prompts.get_grammar_gap_fill_prompt},
        {"type": "grammar_transformation", "method": prompts.get_grammar_transformation_prompt}
    ]
    
    output_file = "example_german_exercises.json"
    all_exercises = []
    
    # Load existing if any
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_exercises = json.load(f)
                print(f"Loaded {len(all_exercises)} existing exercises.")
        except Exception as e:
            print(f"Error loading existing file: {e}")

    # 1. Retrieve German grammar topics from Qdrant
    print("Retrieving German grammar topics from 'Grammar Collection'...")
    try:
        records, _ = qdrant_client.scroll(
            collection_name="Grammar Collection",
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="language",
                        match=MatchValue(value="de")
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False
        )
    except Exception as e:
        print(f"Error connecting to Qdrant or reading collection: {e}")
        return
    
    if not records:
        print("No German grammar topics found in Qdrant! Please run upload_german_grammar.py first.")
        return

    print(f"Found {len(records)} German grammar topics.")
    
    # We want to generate exercises for each level and each retrieved topic
    print(f"Starting generation for German. Goal: {len(levels) * len(records) * len(tasks)} total potential exercises.")
    
    count = len(all_exercises)
    new_count = 0
    
    for level in levels:
        for record in records:
            payload = record.payload
            topic = payload.get('subject', 'German Grammar')
            
            # Use the entire payload content as retrieval context
            # It usually contains definition, structure, examples, etc.
            retrieval_context = json.dumps(payload.get('content', {}), ensure_ascii=False)
            
            for task_info in tasks:
                task_type = task_info["type"]
                generator_method = task_info["method"]
                
                # Check if we already have this combination (simple check)
                exercise_id = f"{topic.lower().replace(' ', '-')}_{task_type}"
                if any(ex.get('id') == exercise_id and ex.get('metadata', {}).get('cefr') == level for ex in all_exercises):
                    # print(f"    Skipping existing: {topic} ({level}) - {task_type}")
                    continue

                print(f"[{new_count+1}] Step 1: Generating {task_type} content for {topic} ({level})...")
                
                section = FormSection(
                    task_type=task_type.split('_')[0], # base type
                    subject=topic,
                    amount=1,
                    additional_comment=f"Create a perfect {task_type} exercise in GERMAN language. Focus on {topic}. Use the provided grammar context for rules and examples."
                )
                
                # Step 1: Generate Raw Content (HTML/Text)
                generation_prompt = generator_method(section, level, "adults", language="German", retrieval=retrieval_context)
                
                try:
                    raw_content = ai_service.ask(generation_prompt)
                    
                    # Step 2: Parse to JSON
                    print(f"    Step 2: Parsing to JSON...")
                    parsing_prompt = prompts.get_exercise_parsing_prompt(raw_content, topic, level, task_type, language="German")
                    
                    json_response = ai_service.ask(parsing_prompt)
                    
                    clean_json = clean_json_response(json_response)
                    exercise_data = json.loads(clean_json)
                    
                    # Ensure metadata is correct
                    exercise_data["language"] = "German"
                    if "metadata" not in exercise_data:
                        exercise_data["metadata"] = {}
                    exercise_data["metadata"]["cefr"] = level
                    exercise_data["metadata"]["subject"] = topic
                    
                    all_exercises.append(exercise_data)
                    new_count += 1
                    count += 1
                    
                    # Periodic save
                    if new_count % 2 == 0:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(all_exercises, f, indent=2, ensure_ascii=False)
                        print(f"--- Saved {count} total exercises ---")
                        
                except Exception as e:
                    print(f"Error during generation/parsing for {topic}/{level}/{task_type}: {e}")
                
                time.sleep(1)

    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_exercises, f, indent=2, ensure_ascii=False)
    
    print(f"Finished! Generated {new_count} new German exercises. Total in file: {count}")

if __name__ == "__main__":
    main()
