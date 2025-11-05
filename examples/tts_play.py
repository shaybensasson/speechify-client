"""Text-to-speech playback from stdin.

Reads text from standard input, synthesizes speech using Speechify API,
and plays the generated audio immediately.

Setup:
    1. Copy .env.example to .env
    2. Add your API key to .env: SPEECHIFY_API_KEY=your-api-key

Usage:
    echo "Hello world" | uv run python examples/tts_play.py
    cat file.txt | uv run python examples/tts_play.py
    uv run python examples/tts_play.py < input.txt

Options:
    --voice-id VOICE_ID  Specify voice ID (default: first available voice)
    --save              Save audio file in addition to playing it
    --quiet             Suppress informational messages

Note:
    Requires 'play' command (from sox package) to play audio.
    Install on Ubuntu/Debian: sudo apt-get install sox
"""

import argparse
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

from rich import print

from speechify_client import SpeechifyClient, SpeechifyError


def play_audio(audio_path: Path, speed: float = 1.25) -> None:
    """Play audio file using the 'play' command.

    Args:
        audio_path: Path to the audio file to play.

    Raises:
        FileNotFoundError: If 'play' command is not found.
        subprocess.CalledProcessError: If playback fails.
    """
    subprocess.run(
        ["play", str(audio_path), "tempo", f"{speed:.2f}"],
        check=True,
        capture_output=True,
        text=True,
    )


def main() -> None:
    """Main function to read stdin, synthesize speech, and play audio."""
    parser = argparse.ArgumentParser(description="Text-to-speech playback from stdin")
    parser.add_argument(
        "--voice-id",
        type=str,
        help="Voice ID to use for synthesis (default: george)",
        default="george",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save audio file to outputs/ directory",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress informational messages",
    )
    parser.add_argument(
        "--speed",
        type=float,
        help="Speed of the speech (default: 1.25)",
        default=1.25,
    )
    args = parser.parse_args()

    # Read text from stdin
    if sys.stdin.isatty():
        print("[red]Error:[/red] No input provided. Please pipe text to stdin.", file=sys.stderr)
        print("[dim]Example: echo 'Hello' | uv run python examples/tts_play.py[/dim]", file=sys.stderr)
        sys.exit(1)

    text = sys.stdin.read().strip()
    if not text:
        print("[red]Error:[/red] Empty input received.", file=sys.stderr)
        sys.exit(1)

    # Initialize the client
    # API key is automatically loaded from .env file via python-dotenv
    client: SpeechifyClient = SpeechifyClient()

    try:
        # Get voice ID
        if args.voice_id:
            voice_id = args.voice_id
            if not args.quiet:
                print(f"[cyan]Using voice:[/cyan] {voice_id}", file=sys.stderr)
        else:
            voices = client.list_voices()
            if not voices:
                print("[red]Error:[/red] No voices available.", file=sys.stderr)
                sys.exit(1)
            voice_id = voices[0].voice_id
            if not args.quiet:
                print(f"[cyan]Using default voice:[/cyan] [bold]{voice_id}[/bold]", file=sys.stderr)

        # Synthesize speech from text
        if not args.quiet:
            preview = text[:50] + "..." if len(text) > 50 else text
            print(f"[yellow]Synthesizing:[/yellow] [italic]{preview}[/italic]", file=sys.stderr)

        response = client.synthesize(
            text=text,
            voice_id=voice_id,
            speed=args.speed,
        )

        if not response.audio_data:
            print("[red]Error:[/red] No audio data received from API.", file=sys.stderr)
            sys.exit(1)

        # Create outputs directory
        # output_dir = Path("outputs")
        # output_dir.mkdir(exist_ok=True)
        output_dir = Path(tempfile.gettempdir())

        # Save audio to temporary file for playback
        output_path = output_dir / "tts_play_output.mp3"
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(response.audio_data))

        if args.save:
            if not args.quiet:
                print(f"[green]✓[/green] Audio saved to [bold]{output_path}[/bold]", file=sys.stderr)
        else:
            if not args.quiet:
                print(f"[dim]Temporary audio: {output_path}[/dim]", file=sys.stderr)

        # Play the audio file
        try:
            if not args.quiet:
                print(f"[magenta]♪[/magenta] Playing audio (speed: {args.speed:.2f})...", file=sys.stderr)
            play_audio(output_path, speed=args.speed)
            if not args.quiet:
                print("[green]✓[/green] Playback completed", file=sys.stderr)
        except FileNotFoundError:
            print(
                "[red]Error:[/red] 'play' command not found. Install sox: [cyan]sudo apt-get install sox[/cyan]",
                file=sys.stderr,
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"[red]Error playing audio:[/red] {e.stderr}", file=sys.stderr)
            sys.exit(1)
        finally:
            # Clean up temporary file if not saving
            if not args.save and output_path.exists():
                output_path.unlink()

    except SpeechifyError as e:
        print(f"[red]Speechify error:[/red] {e.message}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
