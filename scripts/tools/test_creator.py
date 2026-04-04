from backend.app.services.test_generator_service import TestGeneratorService
import questionary
import json
import tkinter as tk
from tkinter import filedialog
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from backend.app.services.json_test_converting_service import JsonTestConvertingService

def main():
    service = TestGeneratorService()
    converting_service = JsonTestConvertingService()
    
    language = questionary.select(
        "Select language",
        choices=["en", "de"]
    ).ask()
    
    level = questionary.select(
        "Select level",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"]
    ).ask()
    
    topic = questionary.text("Enter topic").ask()
    
    group_count_str = questionary.select(
        "Select group count",
        choices=["1", "2", "3", "4"]
    ).ask()
    group_count = int(group_count_str)

    question_count_str = questionary.select(
        "Select question count",
        choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "15"]
    ).ask()
    question_count = int(question_count_str)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}% | {task.completed}/{task.total}"),
        TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("Generating test...", total=1)
        test = service.generate_test(language, level, topic, group_count, question_count)
        progress.update(task, advance=1)

    root = tk.Tk()
    root.withdraw()

    pdf_data = converting_service.convert_to_pdf(test)
    
    path = filedialog.asksaveasfilename(
        title="Save test as PDF",
        defaultextension=".pdf",
        filetypes=[
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
    )

    if path:
        with open(path, "wb") as f:
            f.write(pdf_data)


if __name__ == "__main__":
    main()