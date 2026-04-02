from backend.app.services.data_extraction_service import DataExtractionService
import os
import tkinter as tk
from backend.app.models.schemas import Chunk, ChunkMetadata
from backend.app.services.ai_service import AiService
import hashlib

from tkinter import filedialog
import json
import re
import questionary
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

console = Console()

def main():
    level = questionary.select(
        "Select level:",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"]
    ).ask()

    language = questionary.select(
        "Select language:",
        choices=["en", "de"]
    ).ask()

    section = questionary.select(
        "Select section:",
        choices=["vocab", "gram"]
    ).ask()

    file_name: str = input("Enter file name: ")

    root = tk.Tk()
    root.withdraw()

    extraction_path: str = filedialog.askdirectory(title="Select folder with photos to extract data from")
    print(extraction_path)
    save_path: str = filedialog.askdirectory(title="Select folder to save data to")
    print(save_path)

    service = DataExtractionService()

    image_files = [f for f in os.listdir(extraction_path) if f.endswith((".jpg", ".png"))]

    all_chunks: list[Chunk] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
        TextColumn("[bold green]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting data...", total=len(image_files))

        for filename in image_files:
            path = os.path.join(extraction_path, filename)
            data = service.extract_data(path, section, language)
            
            parsed_data = []
            for d in data:
                try:
                    clean_str = d.strip()
                    if clean_str.startswith("```json"):
                        clean_str = clean_str[7:]
                    elif clean_str.startswith("```"):
                        clean_str = clean_str[3:]
                    if clean_str.endswith("```"):
                        clean_str = clean_str[:-3]
                        
                    parsed_data.append(json.loads(clean_str.strip()))
                except Exception as e:
                    console.print(f"[bold red]Warning: Could not parse AI response as JSON:[/] {e}")

            if not parsed_data:
                console.print(f"[bold red]Error: No valid data extracted from {filename}[/]")
                continue

            subject = parsed_data[0].get("subject", "Unknown")
            
            content = ""
            for slice_data in parsed_data:
                for word in slice_data.get("content", []):
                    content += f"{word.get('word', '')} - {word.get('translation', '')}\n"
            #TODO: ADD CHECKPOINT, BECAUSE WORK CAN BE LOST DURING LONG EXTRACTION PROCESS
            #TODO: OPTIMISE THIS MESS LATER BECAUSE IT TAKES TOO MUCH TIME
            try:
                chunk_section = "vocabulary" if section == "vocab" else "grammar"
                chunk = Chunk(
                    id=hashlib.md5(path.encode()).hexdigest(),
                    section=chunk_section,
                    language=language,
                    level=level,
                    metadata=ChunkMetadata(
                        subject=subject,
                        content=content
                    )
                )
                all_chunks.append(chunk)
            except Exception as e:
                console.print(f"[bold red]Error with file {filename}:[/] {e}")

            progress.advance(task)

    console.print(f"\n[bold green]✓ Done![/] Extracted [cyan]{len(all_chunks)}[/] chunks from [cyan]{len(image_files)}[/] images.")

    with open(os.path.join(save_path, f"{file_name}.json"), "w", encoding="utf-8") as f:
        json.dump([chunk.model_dump() for chunk in all_chunks], f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()