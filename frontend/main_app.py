import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()

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

if __name__ == "__main__":
    main()
