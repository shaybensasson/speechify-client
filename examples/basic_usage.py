"""Basic usage example for Speechify REST client.

This example demonstrates how to initialize the client, synthesize speech,
and retrieve available voices.

Setup:
    1. Copy .env.example to .env
    2. Add your API key to .env: SPEECHIFY_API_KEY=your-api-key
    3. Run: uv run python examples/basic_usage.py

Note:
    Requires 'play' command (from sox package) to play audio.
    Install on Ubuntu/Debian: sudo apt-get install sox
"""

import base64
import logging
import subprocess
from pathlib import Path

from speechify_client import SpeechifyClient, SpeechifyError

# Configure logging to see debug information
logging.basicConfig(level=logging.INFO)

# Initialize the client
# API key is automatically loaded from .env file via python-dotenv
client = SpeechifyClient()

try:
    # List available voices
    voices = client.list_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices[:3]:
        print(f"  - {voice.name} (ID: {voice.voice_id})")

    # Synthesize speech from text
    response = client.synthesize(
        text="Hello! This is a test of the Speechify API.",
        voice_id=voices[0].voice_id,
    )
    print(f"\nSynthesized audio duration: {response.duration} seconds")

    # Save audio to file (example)
    if response.audio_data:
        # Create outputs directory if it doesn't exist
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "basic_usage_output.mp3"
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(response.audio_data))
        print(f"Audio saved to {output_path}")

        # Play the audio file using the 'play' command
        try:
            print("\nPlaying audio file...")
            result = subprocess.run(
                ["play", str(output_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print("Audio playback completed")
        except FileNotFoundError:
            print(
                "Warning: 'play' command not found. "
                "Install sox package to play audio: sudo apt-get install sox"
            )
        except subprocess.CalledProcessError as e:
            print(f"Error playing audio: {e.stderr}")

except SpeechifyError as e:
    print(f"Speechify error: {e.message}")
finally:
    client.close()
