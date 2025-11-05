"""Context manager example for Speechify REST client.

Demonstrates how to use the client as a context manager for automatic
resource cleanup.

Setup:
    1. Copy .env.example to .env
    2. Add your API key to .env: SPEECHIFY_API_KEY=your-api-key
    3. Run: uv run python examples/context_manager.py
"""

from speechify_client import SpeechifyClient

# Use the client as a context manager
# API key is automatically loaded from .env file via python-dotenv
with SpeechifyClient() as client:
    # First, list available voices to get a valid voice_id
    voices = client.list_voices()
    if not voices:
        print("No voices available")
        exit(1)

    # Get details for the first available voice
    voice = client.get_voice(voice_id=voices[0].voice_id)
    print(f"Voice: {voice.name} ({voice.gender})")

    # Synthesize speech
    response = client.synthesize(
        text="Using a context manager ensures proper cleanup.",
        voice_id=voice.voice_id,
    )
    print(f"Duration: {response.duration}s")

# Client session is automatically closed here
print("Client closed automatically")
