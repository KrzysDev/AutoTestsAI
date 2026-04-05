from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.rule import Rule
from rich.columns import Columns
from rich import box
import questionary
from questionary import Style
import sys
import time
import requests
import tkinter as Tk
from tkinter import filedialog

from backend.app.main import app

import uvicorn
import threading

console = Console()

server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="critical"))


# ── Custom questionary style ──────────────────────────────────────────────────
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_success(msg: str) -> None:
    console.print(f"  [bold green]✔[/]  {msg}")

def _print_error(msg: str) -> None:
    console.print(f"  [bold red]✖[/]  {msg}")

def _print_info(msg: str) -> None:
    console.print(f"  [bold cyan]ℹ[/]  {msg}")

def _section(title: str) -> None:
    console.print()
    console.print(Rule(f"[bold magenta] {title} [/]", style="magenta"))
    console.print()


# ── Screens ───────────────────────────────────────────────────────────────────

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

    level = questionary.select(
        "Choose a proficiency level:",
        choices=["A1", "A2", "B1", "B2", "C1", "C2"],
        style=QSTYLE,
    ).ask()

    if level is None:
        return  # user pressed Ctrl+C

    topic = questionary.text(
        "Describe the test topic (be as precise as possible):",
        style=QSTYLE,
    ).ask()

    if topic is None or not topic.strip():
        _print_error("Topic cannot be empty.")
        time.sleep(1.5)
        return

    group_count_raw = questionary.select(
        "How many groups/variants?",
        choices=[
            questionary.Choice("1 group",  value="1"),
            questionary.Choice("2 groups", value="2"),
            questionary.Choice("3 groups", value="3"),
            questionary.Choice("4 groups", value="4"),
        ],
        style=QSTYLE,
    ).ask()

    if group_count_raw is None:
        return

    console.print()

    # ── Step 1: Generate ─────────────────────────────────────────────────────
    generate_url = "http://localhost:8000/v1/rag/test/generate"
    params = {
        "language": "en",
        "level": level,
        "topic": topic,
        "group_count": group_count_raw,
    }

    try:
        with console.status(
            "[bold magenta]Generating test with AI…[/]  [dim](this may take a minute)[/]",
            spinner="dots",
            spinner_style="magenta",
        ):
            response = requests.post(generate_url, params=params, timeout=300)
            response.raise_for_status()
    except requests.exceptions.ConnectionError:
        _print_error("Cannot connect to backend. Is the server running on [bold]localhost:8000[/]?")
        time.sleep(2)
        return
    except requests.exceptions.Timeout:
        _print_error("Request timed out. The model may be overloaded — please try again.")
        time.sleep(2)
        return
    except requests.exceptions.HTTPError as e:
        _print_error(f"Server returned an error: [bold]{e.response.status_code}[/] {e.response.text[:120]}")
        time.sleep(2)
        return

    _print_success(f"Test generated!  [dim]Level:[/] [bold]{level}[/]  [dim]Groups:[/] [bold]{group_count_raw}[/]")

    # ── Step 2: Convert to PDF ───────────────────────────────────────────────
    convert_url = "http://localhost:8000/v1/rag/test/convert"

    try:
        with console.status(
            "[bold cyan]Converting to PDF…[/]",
            spinner="dots2",
            spinner_style="cyan",
        ):
            pdf_response = requests.post(convert_url, json=response.json(), timeout=60)
            pdf_response.raise_for_status()
    except requests.exceptions.ConnectionError:
        _print_error("Lost connection while converting. Please retry.")
        time.sleep(2)
        return
    except requests.exceptions.HTTPError as e:
        _print_error(f"Conversion failed: [bold]{e.response.status_code}[/]")
        time.sleep(2)
        return

    _print_success("PDF ready! Choose where to save it.")
    console.print()

    # ── Step 3: Save ─────────────────────────────────────────────────────────
    try:
        root = Tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        root.destroy()

        if not file_path:
            _print_info("Save cancelled — no file was written.")
            time.sleep(1.5)
            return

        with open(file_path, "wb") as f:
            f.write(pdf_response.content)

        _print_success(f"Saved to [underline cyan]{file_path}[/]")

    except Exception as e:
        _print_error(f"Could not save file: {e}")

    console.print()
    questionary.press_any_key_to_continue("Press any key to return to the menu…").ask()


def print_guide() -> None:
    _section("How to Use AutoTests AI")

    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold magenta",
        border_style="dim",
        padding=(0, 2),
        expand=True,
    )
    table.add_column("Step", style="bold cyan", width=6)
    table.add_column("What to do", style="white")
    table.add_column("Tip", style="dim italic")

    table.add_row(
        "1",
        "Select [bold]Generate Test[/] from the main menu.",
        "You can run multiple tests in one session.",
    )
    table.add_row(
        "2",
        "Pick a CEFR proficiency level (A1 – C2).",
        "Match your students' actual level.",
    )
    table.add_row(
        "3",
        'Enter a [bold]detailed topic[/], e.g. "past simple tense – irregular verbs".',
        "More detail = better test quality.",
    )
    table.add_row(
        "4",
        "Enter the number of [bold]groups / variants[/] you need.",
        "Each group gets a slightly different test.",
    )
    table.add_row(
        "5",
        "Wait for the AI to finish (usually 30–60 s).",
        "Uses AI to generate test.",
    )
    table.add_row(
        "6",
        "Choose a location to [bold]save the PDF[/].",
        "Use a file-picker dialog (ex. Windows file explorer).",
    )

    console.print(table)

    notice = Panel(
        "[yellow]⚠[/]  Currently only [bold]English[/] is supported.\n"
        "Requesting other languages may cause model hallucinations.\n"
        "This software is in [bold]early development[/] — please report any bugs!",
        border_style="yellow",
        padding=(0, 2),
        title="[bold yellow]Notice[/]",
        title_align="left",
    )
    console.print(notice)
    console.print()

    questionary.press_any_key_to_continue("Press any key to go back…").ask()


def navigate_menu() -> None:
    console.clear()
    print_header()
    console.print()

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("⚡  Generate Test", value="generate"),
            questionary.Choice("📖  How to Use", value="guide"),
            questionary.Choice("🚪  Exit", value="exit"),
        ],
        style=QSTYLE,
    ).ask()

    if choice == "generate":
        generate_test()
    elif choice == "guide":
        print_guide()
    elif choice == "exit" or choice is None:
        server.should_exit = True
        console.print()
        console.print(Panel(
            "[bold white]Thank you for using [magenta]AutoTests AI[/magenta]! 👋[/]",
            border_style="magenta",
            padding=(0, 4),
        ))
        console.print()
        sys.exit(0)



def main() -> None:
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while True:
        navigate_menu()


if __name__ == "__main__":
    main()
