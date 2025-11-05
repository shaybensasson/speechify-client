"""List available Speechify voices.

Retrieves and displays all available voices from the Speechify API
with formatted output using rich.

Setup:
    1. Copy .env.example to .env
    2. Add your API key to .env: SPEECHIFY_API_KEY=your-api-key

Usage:
    uv run python examples/list_voices.py
    uv run python examples/list_voices.py --format table
    uv run python examples/list_voices.py --format json
"""

import argparse
import json
import sys

from rich import print
from rich.console import Console
from rich.table import Table

from speechify_client import SpeechifyClient, SpeechifyError


def display_table(voices: list) -> None:
    """Display voices in a formatted table.

    Args:
        voices: List of Voice objects from the API.
    """
    console = Console()

    table = Table(
        title="[bold cyan]Available Speechify Voices[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Voice ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Gender", style="yellow")
    table.add_column("Language", style="blue")

    for voice in voices:
        table.add_row(
            voice.voice_id or "",
            voice.name or "-",
            voice.gender or "-",
            voice.language or "-",
        )

    console.print(table)
    console.print(f"\n[dim]Total voices: {len(voices)}[/dim]")


def display_list(voices: list) -> None:
    """Display voices as a simple list.

    Args:
        voices: List of Voice objects from the API.
    """
    print(f"[bold cyan]Available Voices ({len(voices)}):[/bold cyan]\n")

    for i, voice in enumerate(voices, 1):
        voice_id = voice.voice_id or "unknown"
        name = voice.name or "-"
        gender = voice.gender or "-"
        language = voice.language or "-"

        print(f"{i:4d}. [cyan]{voice_id:20s}[/cyan] "
              f"[green]{name:20s}[/green] "
              f"[yellow]{gender:10s}[/yellow] "
              f"[blue]{language}[/blue]")


def display_json(voices: list) -> None:
    """Display voices as JSON.

    Args:
        voices: List of Voice objects from the API.
    """
    voices_data = [voice.to_dict() for voice in voices]
    print(json.dumps(voices_data, indent=2))


def main() -> None:
    """Main function to list available voices."""
    parser = argparse.ArgumentParser(
        description="List available Speechify voices"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["table", "list", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of voices to display",
    )
    args = parser.parse_args()

    # Initialize the client
    # API key is automatically loaded from .env file via python-dotenv
    try:
        client = SpeechifyClient()
    except Exception as e:
        print(f"[red]Error initializing client:[/red] {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Get all voices
        print("[yellow]Fetching voices...[/yellow]", file=sys.stderr)
        voices = client.list_voices()

        if not voices:
            print("[red]No voices available.[/red]", file=sys.stderr)
            sys.exit(1)

        # Apply limit if specified
        if args.limit and args.limit > 0:
            voices = voices[:args.limit]

        # Display voices in requested format
        if args.format == "table":
            display_table(voices)
        elif args.format == "list":
            display_list(voices)
        elif args.format == "json":
            display_json(voices)

    except SpeechifyError as e:
        print(f"[red]Speechify error:[/red] {e.message}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
