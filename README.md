# Speechify REST Client

A simple, type-safe REST client for the Speechify AI Text-to-Speech API.

## Features

- **Text-to-Speech Synthesis**: Convert text to high-quality speech using Speechify's AI models
- **Voice Management**: List and retrieve details about available voices
- **Authentication**: Supports both API keys and access tokens
- **Error Handling**: Comprehensive exception handling with specific error types
- **Logging**: Built-in logging for debugging and monitoring
- **Type Hints**: Full type annotations for IDE support and type checking
- **Context Manager**: Automatic resource cleanup with `with` statement

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install the project and its dependencies
uv sync

# Or install with dev dependencies
uv sync --dev
```

## Quick Start

### Basic Usage

```python
from speechify_client import SpeechifyClient

# Initialize the client
# API key is automatically loaded from .env file
client = SpeechifyClient()

# Get available voices
voices = client.list_voices()
print(f"Available voices: {len(voices)}")

# Synthesize speech
response = client.synthesize(
    text="Hello, world!",
    voice_id=voices[0].voice_id
)

# Save the audio
import base64
from pathlib import Path

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

with open(output_dir / "output.mp3", "wb") as f:
    f.write(base64.b64decode(response.audio_data))
```

### Using a Context Manager

```python
from speechify_client import SpeechifyClient

# API key is automatically loaded from .env file
with SpeechifyClient() as client:
    voices = client.list_voices()
    response = client.synthesize(
        text="Hello!",
        voice_id=voices[0].voice_id
    )
# Client session is automatically closed
```

### Using Access Tokens

```python
from speechify_client import SpeechifyClient

# API key is automatically loaded from .env file
client = SpeechifyClient()

# Create an access token
token = client.create_access_token()

# Token is automatically used for subsequent requests
voices = client.list_voices()
response = client.synthesize(
    text="Using access token",
    voice_id=voices[0].voice_id
)
```

## Configuration

### API Key

Set your API key using one of these methods:

1. **Using .env file** (recommended):
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
echo "SPEECHIFY_API_KEY=your-api-key" > .env
```

The client automatically loads environment variables from `.env` using python-dotenv.

2. **Environment Variable**:
```bash
export SPEECHIFY_API_KEY="your-api-key"
```

3. **Constructor Parameter** (not recommended, use .env instead):
```python
# Only use this for testing or when .env is not available
client = SpeechifyClient(api_key="your-api-key")
```

### Timeout

Customize the request timeout (default: 30 seconds):

```python
# API key loaded from .env, custom timeout
client = SpeechifyClient(timeout=60)
```

## API Methods

### `synthesize(text, voice_id, audio_format="mp3")`

Synthesize speech from text.

**Parameters:**
- `text` (str): Text to synthesize
- `voice_id` (str): ID of the voice to use
- `audio_format` (str): Audio format (default: "mp3")

**Returns:** `SpeechSynthesisResponse` containing audio data and metadata

**Raises:** `ValidationError`, `APIError`

### `list_voices()`

Get a list of all available voices.

**Returns:** List of `Voice` objects

**Raises:** `APIError`

### `get_voice(voice_id)`

Get details for a specific voice.

**Parameters:**
- `voice_id` (str): ID of the voice to retrieve

**Returns:** `Voice` object

**Raises:** `ValidationError`, `APIError`

### `create_access_token()`

Create an access token from the API key.

**Returns:** `AccessToken` object

**Raises:** `APIError`

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from speechify_client import SpeechifyClient
from speechify_client.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    SpeechifyError
)

try:
    # API key loaded from .env
    client = SpeechifyClient()
    voices = client.list_voices()
    response = client.synthesize(text="Hello", voice_id=voices[0].voice_id)
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
except SpeechifyError as e:
    print(f"Unexpected error: {e.message}")
```

## Logging

Enable logging to see debug information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Log messages include API requests, responses, and error details.

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py`: Simple example with voice listing and synthesis
- `context_manager.py`: Using the client as a context manager
- `access_token.py`: Creating and using access tokens
- `tts_play.py`: Command-line tool for synthesizing and playing speech from stdin

### Command-Line TTS Playback (`tts_play.py`)

The `tts_play.py` script reads text from standard input, synthesizes speech using the Speechify API, and plays the generated audio immediately. This is useful for quick text-to-speech conversion from the command line.

**Prerequisites:**

Install the `sox` package for audio playback:

```bash
# Ubuntu/Debian
sudo apt-get install sox

# macOS (using Homebrew)
brew install sox
```

**Basic Usage:**

```bash
# Read from echo
echo "Hello world" | uv run python examples/tts_play.py

# Read from a file
cat file.txt | uv run python examples/tts_play.py

# Read from stdin redirect
uv run python examples/tts_play.py < input.txt
```

**Options:**

- `--voice-id VOICE_ID`: Specify the voice ID to use (default: "george")
- `-q, --quiet`: Suppress informational messages
- `--save`: Save the audio file in addition to playing it (saves to system temp directory)
- `--speed SPEED`: Set the playback speed (default: 1.25)

**Examples:**

```bash
# Use a specific voice
echo "Testing voice" | uv run python examples/tts_play.py --voice-id george

# Save audio file while playing
echo "Save this audio" | uv run python examples/tts_play.py --save

# Quiet mode (no informational output)
echo "Silent playback" | uv run python examples/tts_play.py -q

# Custom playback speed
echo "Faster speech" | uv run python examples/tts_play.py --speed 1.5

# Combine options
cat long_text.txt | uv run python examples/tts_play.py --voice-id george --speed 1.3 --save
```

**Note:** The script automatically loads your API key from the `.env` file. Make sure you have set `SPEECHIFY_API_KEY` in your `.env` file before running the script.

## Testing

Run the test suite using uv:

```bash
uv run pytest tests/
```

With coverage:

```bash
uv run pytest tests/ --cov=speechify_client
```

## Development

### Running Scripts

Use `uv run` to execute Python scripts:

```bash
uv run python examples/basic_usage.py
```

### Code Quality

Check code with ruff:

```bash
uv run ruff check speechify_client/ tests/ examples/
```

Format code:

```bash
uv run ruff format speechify_client/ tests/ examples/
```

## API Reference

For detailed API documentation, visit the [Speechify API docs](https://docs.sws.speechify.com).

## License

MIT
