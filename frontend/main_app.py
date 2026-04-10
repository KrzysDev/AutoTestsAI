import questionary
from rich.console import Console
from rich.panel import Panel
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.services.json_test_converting_service import JsonTestConvertingService
from backend.app.models.schemas import GeneratedTest

console = Console()

# <summary>
# Mock CLI Frontend representing the user interaction point.
# Captures user settings and orchestrates the backend test generation services.
# </summary>
def main():
    console.print(Panel.fit("[bold green]AutoTests AI[/bold green]", border_style="green"))

    cefr_level = questionary.select(
        "Choose CEFR level:",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"]
    ).ask()

    age_group = questionary.select(
        "Age category:",
        choices=["kids", "teens", "adults"]
    ).ask()

    task_count = questionary.text(
        "Exercises in total:",
        validate=lambda text: text.isdigit() and int(text) > 0
    ).ask()

    prompt_query = questionary.text(
        "Say anything you want me to make....(prompt):"
    ).ask()

    console.print(Panel(
        f"CEFR: {cefr_level}\n"
        f"Grupa wiekowa: {age_group}\n"
        f"Ilość zadań: {task_count}\n"
        f"Zapytanie: {prompt_query}",
        title="[bold blue]Zapisane dane[/bold blue]",
        expand=False
    ))

    console.print("[bold yellow]Generating test, please wait...[/bold yellow]")

    try:
        generator = TestGeneratorService()
        converter = JsonTestConvertingService()
        
        # Generowanie testu
        generated_test_json_str = generator.generate_test(
            prompt=prompt_query,
            level=cefr_level,
            age_group=age_group,
            total_amount=int(task_count)
        )
        
        # Przetworzenie otrzymanego stringa na obiekt
        test_dict = json.loads(generated_test_json_str)
        test_obj = GeneratedTest.model_validate(test_dict)
        
        console.print("[bold green]Test generated successfully! Saving outputs...[/bold green]")
        
        converter.save_to_json(test_obj, "wygenerowany_test.json")
        pdf_bytes = converter.convert_to_pdf(test_obj)
        
        with open("wygenerowany_test.pdf", "wb") as f:
            f.write(pdf_bytes)
            
        console.print("[bold green]Successfully saved 'wygenerowany_test.json' and 'wygenerowany_test.pdf'![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Failed to generate test:[/bold red] {e}")

if __name__ == "__main__":
    main()
