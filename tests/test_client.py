"""Tests for Speechify REST client."""

import os
from unittest.mock import patch

import pytest

from speechify_client import SpeechifyClient
from speechify_client.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
)
from speechify_client.models import AccessToken, SpeechSynthesisResponse


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key"


@pytest.fixture
def client(api_key):
    """Create a Speechify client for testing."""
    return SpeechifyClient(api_key=api_key)


def test_client_initialization_with_api_key(api_key):
    """Test client initialization with explicit API key."""
    client = SpeechifyClient(api_key=api_key)
    assert client.api_key == api_key


def test_client_initialization_from_env():
    """Test client initialization from environment variable."""
    with patch.dict(os.environ, {"SPEECHIFY_API_KEY": "env-key"}):
        client = SpeechifyClient()
        assert client.api_key == "env-key"


def test_client_initialization_missing_api_key():
    """Test client initialization fails without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError) as exc_info:
            SpeechifyClient()
        assert "API key not provided" in str(exc_info.value)


def test_get_headers_with_api_key(client, api_key):
    """Test header generation with API key."""
    headers = client._get_headers()
    assert headers["Authorization"] == f"Bearer {api_key}"
    assert headers["Content-Type"] == "application/json"


def test_get_headers_with_access_token(client):
    """Test header generation with access token."""
    client._access_token = "access-token"
    headers = client._get_headers(use_access_token=True)
    assert headers["Authorization"] == "Bearer access-token"


@patch("speechify_client.client.requests.Session.request")
def test_synthesize_success(mock_request, client):
    """Test successful speech synthesis."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {
        "audioData": "base64encodedaudio==",
        "duration": 2.5,
        "sampleRate": 44100,
        "format": "mp3",
    }

    response = client.synthesize(text="Hello world", voice_id="voice-123")

    assert isinstance(response, SpeechSynthesisResponse)
    assert response.audio_data == "base64encodedaudio=="
    assert response.duration == 2.5
    mock_request.assert_called_once()


def test_synthesize_empty_text(client):
    """Test synthesis with empty text."""
    with pytest.raises(ValidationError) as exc_info:
        client.synthesize(text="", voice_id="voice-123")
    assert "cannot be empty" in str(exc_info.value)


def test_synthesize_empty_voice_id(client):
    """Test synthesis with empty voice ID."""
    with pytest.raises(ValidationError) as exc_info:
        client.synthesize(text="Hello", voice_id="")
    assert "Voice ID cannot be empty" in str(exc_info.value)


@patch("speechify_client.client.requests.Session.request")
def test_synthesize_api_error(mock_request, client):
    """Test synthesis with API error response."""
    mock_request.return_value.status_code = 400
    mock_request.return_value.json.return_value = {"message": "Invalid voice ID"}

    with pytest.raises(APIError) as exc_info:
        client.synthesize(text="Hello", voice_id="invalid")
    assert exc_info.value.status_code == 400


@patch("speechify_client.client.requests.Session.request")
def test_synthesize_authentication_error(mock_request, client):
    """Test synthesis with authentication error."""
    mock_request.return_value.status_code = 401

    with pytest.raises(AuthenticationError):
        client.synthesize(text="Hello", voice_id="voice-123")


@patch("speechify_client.client.requests.Session.request")
def test_list_voices_success(mock_request, client):
    """Test successful voice listing with dict response."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {
        "voices": [
            {
                "id": "voice-1",
                "name": "Alex",
                "gender": "male",
                "language": "en-US",
            },
            {
                "id": "voice-2",
                "name": "Victoria",
                "gender": "female",
                "language": "en-US",
            },
        ]
    }

    voices = client.list_voices()

    assert len(voices) == 2
    assert voices[0].voice_id == "voice-1"
    assert voices[0].name == "Alex"
    assert voices[1].voice_id == "voice-2"


@patch("speechify_client.client.requests.Session.request")
def test_list_voices_success_list_response(mock_request, client):
    """Test successful voice listing with list response."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = [
        {
            "id": "voice-1",
            "name": "Alex",
            "gender": "male",
            "language": "en-US",
        },
        {
            "id": "voice-2",
            "name": "Victoria",
            "gender": "female",
            "language": "en-US",
        },
    ]

    voices = client.list_voices()

    assert len(voices) == 2
    assert voices[0].voice_id == "voice-1"
    assert voices[0].name == "Alex"
    assert voices[1].voice_id == "voice-2"


@patch("speechify_client.client.requests.Session.request")
def test_get_voice_success(mock_request, client):
    """Test successful voice retrieval."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {
        "id": "voice-123",
        "name": "Alex",
        "gender": "male",
        "language": "en-US",
    }

    voice = client.get_voice(voice_id="voice-123")

    assert voice.voice_id == "voice-123"
    assert voice.name == "Alex"
    assert voice.gender == "male"


def test_get_voice_empty_voice_id(client):
    """Test get_voice with empty voice ID."""
    with pytest.raises(ValidationError) as exc_info:
        client.get_voice(voice_id="")
    assert "Voice ID cannot be empty" in str(exc_info.value)


@patch("speechify_client.client.requests.Session.request")
def test_create_access_token(mock_request, client):
    """Test access token creation."""
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {
        "access_token": "new-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "audio:speech",
    }

    token = client.create_access_token()

    assert isinstance(token, AccessToken)
    assert token.access_token == "new-token"
    assert client._access_token == "new-token"


@patch("speechify_client.client.requests.Session.close")
def test_close_client(mock_close, client):
    """Test closing the client."""
    client.close()
    mock_close.assert_called_once()


def test_context_manager(api_key):
    """Test client as context manager."""
    with patch("speechify_client.client.requests.Session.close"):
        with SpeechifyClient(api_key=api_key) as client:
            assert client.api_key == api_key


@patch("speechify_client.client.requests.Session.request")
def test_make_request_network_error(mock_request, client):
    """Test request handling for network errors."""
    import requests

    mock_request.side_effect = requests.ConnectionError("Network error")

    with pytest.raises(APIError) as exc_info:
        client.list_voices()
    assert "Request failed" in str(exc_info.value)


@patch("speechify_client.client.requests.Session.request")
def test_make_request_invalid_json(mock_request, client):
    """Test request handling for invalid JSON response."""
    mock_request.return_value.status_code = 500
    mock_request.return_value.json.side_effect = ValueError("Invalid JSON")
    mock_request.return_value.text = "Internal Server Error"

    with pytest.raises(APIError) as exc_info:
        client.list_voices()
    assert exc_info.value.status_code == 500
