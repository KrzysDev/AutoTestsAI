from backend.app.models.prompts import SystemPrompts

def main():
    prompts = SystemPrompts()
    print(prompts.get_test_generation_prompt("en", "B2", [], "test", "test", 1))

if __name__ == "__main__":
    main()