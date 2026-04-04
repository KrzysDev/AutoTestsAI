from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import questionary
import sys
import requests
import tkinter as Tk
from tkinter import filedialog

console = Console()

def generate_test():
    console.print("Alright let's generate a english test!")

    level = questionary.select(
        "Choose a level:",
        choices=[
            "A1",
            "A2",
            "B1",
            "B2",
            "C1",
            "C2",
        ],
    ).ask()

    topic = questionary.text("Enter a topic (describe a test as precisly as possible):").ask()

    group_count = questionary.text("Enter a number of groups:").ask()

    generate_url = "http://localhost:8000/v1/rag/test/generate"

    params = {
        "language": "en",
        "level": level,
        "topic": topic,
        "group_count": group_count,
    }

    response = requests.post(generate_url, params=params)

    convert_url = "http://localhost:8000/v1/rag/test/convert"

    json_conver_response = requests.post(convert_url, json=response.json())

    try:
        console.print("Test generated successfully!")
        console.print("now where would you like to save your test?")

        Tk.Tk().withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=["PDF files", "All files"],
        )

        with open(file_path, "wb") as f:
            f.write(json_conver_response.content)

        console.print(f"Test saved to {file_path}")
    except Exception as e:
        console.print(f"Error generating test: {e}")

    

def navigate_menu():
    choice = questionary.select(
        "Choose an option:",
        choices=[
            "Generate Test",
            "How to use",
            "Exit",
        ],
    ).ask()

    if choice == "Generate Test":
        console.print("You chose Option 1")
        generate_test()
    elif choice == "How to use":
        console.print("You chose Option 2")
    elif choice == "Exit":
        sys.exit()


def main():
    console = Console()

    title = Text("AutoTests AI", style="bold magenta")
    subtitle = Text("AI Test Generator for Teachers", style="dim")

    console.print(
        Panel(
            Text.assemble(title, "\n", subtitle),
            border_style="magenta",
            padding=(1, 4),
        )
    )

    while True:
        navigate_menu()

    
if __name__ == "__main__":
    main()



