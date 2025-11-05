"""Access token example for Speechify REST client.

Demonstrates how to create and use access tokens for API authentication.

Setup:
    1. Copy .env.example to .env
    2. Add your API key to .env: SPEECHIFY_API_KEY=your-api-key
    3. Run: uv run python examples/access_token.py
"""

from speechify_client import SpeechifyClient

# Initialize the client
# API key is automatically loaded from .env file via python-dotenv
client = SpeechifyClient()

try:
    # Create an access token from your API key
    token_response = client.create_access_token()
    print("Access token created successfully")
    print(f"Token type: {token_response.token_type}")
    print(f"Expires in: {token_response.expires_in} seconds")

    # The token is automatically used for subsequent requests
    # You can verify this by checking client._access_token

    # Get available voices to use for synthesis
    voices = client.list_voices()
    if not voices:
        print("No voices available")
        exit(1)

    # Synthesize speech using the access token
    response = client.synthesize(
        text="This request uses the access token for authentication.",
        voice_id=voices[0].voice_id,
    )
    print(f"\nSynthesis successful! Duration: {response.duration}s")

except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
