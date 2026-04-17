from backend.app.models.prompts import SystemPrompts

prompts = SystemPrompts()

print(prompts.get_parsing_prompt("Wygeneruj test powtorzeniowy dla klasy maturalnej ze wszystkich czasow"))

