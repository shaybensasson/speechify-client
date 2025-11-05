"""Tests for Speechify data models."""

from speechify_client.models import (
    AccessToken,
    SpeechSynthesisRequest,
    SpeechSynthesisResponse,
    Voice,
)


def test_voice_creation():
    """Test Voice model creation."""
    voice = Voice(voice_id="v1", name="Alex", gender="male")
    assert voice.voice_id == "v1"
    assert voice.name == "Alex"
    assert voice.gender == "male"


def test_voice_to_dict():
    """Test Voice to_dict method."""
    voice = Voice(voice_id="v1", name="Alex", gender="male", language=None)
    voice_dict = voice.to_dict()
    assert voice_dict["voice_id"] == "v1"
    assert voice_dict["name"] == "Alex"
    assert "language" not in voice_dict


def test_speech_synthesis_request_to_dict():
    """Test SpeechSynthesisRequest to_dict method."""
    request = SpeechSynthesisRequest(
        input_text="Hello world",
        voice_id="v1",
        audio_format="mp3",
        emotion=None,
    )
    request_dict = request.to_dict()
    assert request_dict["input"] == "Hello world"
    assert request_dict["voice_id"] == "v1"
    assert request_dict["audio_format"] == "mp3"
    assert "emotion" not in request_dict


def test_speech_synthesis_response_from_dict_camel_case():
    """Test SpeechSynthesisResponse from_dict with camelCase keys."""
    data = {
        "audioData": "base64==",
        "duration": 2.5,
        "sampleRate": 44100,
        "format": "mp3",
    }
    response = SpeechSynthesisResponse.from_dict(data)
    assert response.audio_data == "base64=="
    assert response.duration == 2.5
    assert response.sample_rate == 44100


def test_speech_synthesis_response_from_dict_snake_case():
    """Test SpeechSynthesisResponse from_dict with snake_case keys."""
    data = {
        "audio_data": "base64==",
        "duration": 2.5,
        "sample_rate": 44100,
        "format": "mp3",
    }
    response = SpeechSynthesisResponse.from_dict(data)
    assert response.audio_data == "base64=="
    assert response.duration == 2.5


def test_access_token_from_dict():
    """Test AccessToken from_dict method."""
    data = {
        "access_token": "abc.def.xyz",
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": "audio:speech",
    }
    token = AccessToken.from_dict(data)
    assert token.access_token == "abc.def.xyz"
    assert token.token_type == "bearer"
    assert token.expires_in == 3600
    assert token.scope == "audio:speech"


def test_access_token_from_dict_minimal():
    """Test AccessToken from_dict with minimal data."""
    data = {"access_token": "token"}
    token = AccessToken.from_dict(data)
    assert token.access_token == "token"
    assert token.token_type == "bearer"
    assert token.expires_in == 3600
