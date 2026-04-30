import sys
import os
import json
import time

# Add backend to path so we can import models and services
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import FormSection
from backend.app.utils.json_utils import clean_json_response

def main():
    ai_service = AiService()
    prompts = SystemPrompts()
    
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    
    # Define tasks with their specific generator methods
    tasks = [
        {"type": "grammar_mcq", "method": prompts.get_grammar_mcq_prompt},
        {"type": "grammar_gap_fill", "method": prompts.get_grammar_gap_fill_prompt},
        {"type": "grammar_transformation", "method": prompts.get_grammar_transformation_prompt},
        {"type": "vocabulary_matching", "method": prompts.get_vocabulary_matching_prompt},
        {"type": "writing_email", "method": prompts.get_writing_email_prompt},
        {"type": "writing_essay", "method": prompts.get_writing_essay_prompt}
    ]
    
    # 12 tenses + 4 vocab topics = 16 topics
    topics = [
        "Present Simple", "Present Continuous", "Present Perfect", "Present Perfect Continuous",
        "Past Simple", "Past Continuous", "Past Perfect", "Past Perfect Continuous",
        "Future Simple", "Future Continuous", "Future Perfect", "Future Perfect Continuous",
        "Family and Relationships", "Travel and Tourism", "Food and Cooking", "Technology and Science"
    ]
    
    output_file = "example_exercises.json"
    all_exercises = []
    
    # Load existing if any
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_exercises = json.load(f)
        except:
            pass

    print(f"Starting two-step generation. Goal: {len(levels) * len(topics)} iterations with multiple task variants.")
    
    count = 0
    for level in levels:
        for topic in topics:
            # For each topic and level, we might want to generate a few relevant task types
            # To keep it manageable, let's pick 2-3 random relevant types or just rotate them
            
            is_grammar_topic = any(tense in topic for tense in ["Present", "Past", "Future"])
            
            # Select relevant tasks
            if is_grammar_topic:
                relevant_tasks = [t for t in tasks if "grammar" in t["type"]]
            else:
                relevant_tasks = [t for t in tasks if "vocabulary" in t["type"] or "writing" in t["type"]]
            
            for task_info in relevant_tasks:
                task_type = task_info["type"]
                generator_method = task_info["method"]
                
                print(f"[{count+1}] Step 1: Generating {task_type} content for {topic} ({level})...")
                
                section = FormSection(
                    task_type=task_type.split('_')[0], # base type
                    subject=topic,
                    amount=1,
                    additional_comment=f"Create a perfect {task_type} exercise."
                )
                
                # Step 1: Generate Raw Content (HTML/Text)
                generation_prompt = generator_method(section, level, "adults")
                try:
                    raw_content = ai_service.ask(generation_prompt)
                    
                    # Step 2: Parse to JSON
                    print(f"    Step 2: Parsing to JSON...")
                    parsing_prompt = prompts.get_exercise_parsing_prompt(raw_content, topic, level, task_type)
                    json_response = ai_service.ask(parsing_prompt)
                    
                    clean_json = clean_json_response(json_response)
                    exercise_data = json.loads(clean_json)
                    
                    all_exercises.append(exercise_data)
                    count += 1
                    
                    # Periodic save
                    if count % 2 == 0: # Save more frequently due to 2-step process
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(all_exercises, f, indent=2, ensure_ascii=False)
                        print(f"--- Saved {count} exercises ---")
                        
                except Exception as e:
                    print(f"Error during generation/parsing for {topic}/{level}/{task_type}: {e}")
                
                time.sleep(1)

    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_exercises, f, indent=2, ensure_ascii=False)
    
    print(f"Finished! Generated {count} exercises in total.")

if __name__ == "__main__":
    main()
