from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box
import questionary
from questionary import Style
import sys
import requests

from backend.app.main import app
from backend.app.services.json_test_converting_service import JsonTestConvertingService
from backend.app.models.schemas import GeneratedTestSection

import uvicorn
import threading
import time

console = Console()

server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error"))

import logging

logging.getLogger("sentence-transformers").setLevel(logging.ERROR)

QSTYLE = Style(
    [
        ("qmark", "fg:#a78bfa bold"),
        ("question", "bold"),
        ("answer", "fg:#86efac bold"),
        ("pointer", "fg:#a78bfa bold"),
        ("highlighted", "fg:#a78bfa bold"),
        ("selected", "fg:#86efac"),
        ("separator", "fg:#6b7280"),
        ("instruction", "fg:#6b7280 italic"),
    ]
)


def _print_success(msg: str) -> None:
    console.print(f"  [bold green]✔[/]  {msg}")

def _print_error(msg: str) -> None:
    console.print(f"  [bold red]✖[/]  {msg}")

def _section(title: str) -> None:
    console.print()
    console.print(Rule(f"[bold magenta] {title} [/]", style="magenta"))
    console.print()


def print_header() -> None:
    title = Text()
    title.append("Auto", style="bold white")
    title.append("Tests", style="bold magenta")
    title.append(" AI", style="bold white")

    subtitle = Text("AI-powered Test Generator for Language Teachers", style="dim white")

    badge_row = Text()
    badge_row.append("  ", style="")
    badge_row.append("  🎓 English • Grammar • Vocabulary  ", style="on #1e1b4b white")

    console.print(
        Panel(
            Text.assemble(title, "\n", subtitle, "\n\n", badge_row),
            border_style="magenta",
            padding=(1, 6),
            box=box.DOUBLE_EDGE,
        )
    )


def generate_test() -> None:
    _section("Generate New Test")

    topic = questionary.text(
        "Describe the test topic (be as precise as possible):",
        style=QSTYLE,
    ).ask()

    if topic is None or not topic.strip():
        _print_error("Topic cannot be empty.")
        return

    console.print()

    try:
        with console.status(
            "[bold magenta]Generating test with AI…[/]  [dim](this may take a minute)[/]",
            spinner="dots",
            spinner_style="magenta",
        ):
            response = requests.post(
                f"http://{server.config.host}:{server.config.port}/v1/rag/test/generate",
                params={"topic": topic},
                timeout=300,
            )
            response.raise_for_status()
            
    except requests.exceptions.ConnectionError:
        _print_error("Cannot connect to backend. Is the server running on [bold]localhost:8000[/]?")
        return
    except requests.exceptions.Timeout:
        _print_error("Request timed out. The model may be overloaded — please try again.")
        return
    except requests.exceptions.HTTPError as e:
        _print_error(f"Server returned an error: [bold]{e.response.status_code}[/]")
        print(e.response.text)
        return

    _print_success("Done!")
    console.print()
    
    data = response.json()
    console.print(Panel(
        str(data),
        border_style="magenta",
        title="[bold]Response[/]",
        padding=(1, 2),
    ))
    console.print()

    try:
        sections = [GeneratedTestSection.model_validate(item) for item in data]
        converting_service = JsonTestConvertingService()
        
        json_path = "wygenerowany_test.json"
        pdf_path = "wygenerowany_test.pdf"
        
        converting_service.save_to_json(sections, filepath=json_path)
        
        pdf_bytes = converting_service.convert_to_pdf(sections)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
            
        _print_success(f"Saved files to [bold]{json_path}[/] and [bold]{pdf_path}[/]")
    except Exception as e:
        _print_error(f"Could not save files: {e}")

    console.print()
    questionary.press_any_key_to_continue("Press any key to return to the menu…").ask()


def shutdown() -> None:
    server.should_exit = True
    console.print()
    console.print(Panel(
        "[bold white]Thank you for using [magenta]AutoTests AI[/magenta]! 👋[/]",
        border_style="magenta",
        padding=(0, 4),
    ))
    console.print()


def navigate_menu() -> bool:
    console.clear()
    print_header()
    console.print()

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("⚡  Generate Test", value="generate"),
            questionary.Choice("🚪  Exit", value="exit"),
        ],
        
        style=QSTYLE,
    ).ask()

    if choice == "generate":
        generate_test()
        return True
    elif choice == "exit" or choice is None:
        return False
    
    return True


def main() -> None:
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        while True:
            if not navigate_menu():
                break
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


if __name__ == "__main__":
    main()