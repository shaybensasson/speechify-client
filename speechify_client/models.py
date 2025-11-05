"""Data models for Speechify API requests and responses."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Voice:
    """Voice metadata from Speechify API."""

    voice_id: str
    name: str
    gender: str | None = None
    language: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SpeechSynthesisRequest:
    """Request parameters for speech synthesis."""

    input_text: str
    voice_id: str
    audio_format: str = "mp3"
    sample_rate: int | None = None
    style: str | None = None
    emotion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {
            k: v
            for k, v in asdict(self).items()
            if v is not None and k != "input_text"
        } | {"input": self.input_text}


@dataclass
class SpeechSynthesisResponse:
    """Response from speech synthesis API."""

    audio_data: str
    duration: float | None = None
    sample_rate: int | None = None
    format: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpeechSynthesisResponse":
        """Create from API response dictionary."""
        return cls(
            audio_data=data.get("audioData", data.get("audio_data", "")),
            duration=data.get("duration"),
            sample_rate=data.get("sample_rate", data.get("sampleRate")),
            format=data.get("format"),
        )


@dataclass
class AccessToken:
    """Access token response from authentication."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccessToken":
        """Create from API response dictionary."""
        return cls(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in", 3600),
            scope=data.get("scope"),
        )
