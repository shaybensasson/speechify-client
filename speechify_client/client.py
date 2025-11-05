"""Speechify REST client for text-to-speech synthesis API."""

import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv

from speechify_client.exceptions import APIError, AuthenticationError, ValidationError
from speechify_client.models import (
    AccessToken,
    SpeechSynthesisRequest,
    SpeechSynthesisResponse,
    Voice,
)

# Load environment variables from .env file
load_dotenv()

_logger = logging.getLogger(__name__)

SCRIPT_NAME = "speechify_client"
API_BASE_URL = "https://api.sws.speechify.com/v1"
DEFAULT_TIMEOUT = 30


class SpeechifyClient:
    """REST client for Speechify AI API.

    Provides methods for text-to-speech synthesis, voice management,
    and authentication with the Speechify API.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize Speechify REST client.

        Args:
            api_key: Speechify API key. Defaults to SPEECHIFY_API_KEY env var.
            timeout: Request timeout in seconds.

        Raises:
            ValidationError: If API key is not provided or found.
        """
        self.api_key = api_key or os.getenv("SPEECHIFY_API_KEY")
        if not self.api_key:
            raise ValidationError(
                message="Speechify API key not provided. Set SPEECHIFY_API_KEY "
                "environment variable or pass api_key parameter."
            )

        self.timeout = timeout
        self.base_url = API_BASE_URL
        self._access_token: str | None = None
        self._session = requests.Session()
        _logger.debug("Initialized Speechify client")

    def _get_headers(self, *, use_access_token: bool = False) -> dict[str, str]:
        """Get request headers with authentication.

        Args:
            use_access_token: Use access token instead of API key.

        Returns:
            Dictionary of HTTP headers.
        """
        token = self._access_token if use_access_token and self._access_token else self.api_key
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _make_request(
        self,
        *,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        use_access_token: bool = False,
    ) -> dict[str, Any]:
        """Make HTTP request to Speechify API.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            json_data: JSON body for POST/PUT requests.
            use_access_token: Use access token for authentication.

        Returns:
            Parsed JSON response.

        Raises:
            AuthenticationError: If authentication fails.
            APIError: If API request fails.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(use_access_token=use_access_token)

        try:
            response = self._session.request(
                method,
                url,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
            )
            _logger.debug(f"API request: {method} {endpoint} - {response.status_code}")

            if response.status_code == 401:
                raise AuthenticationError(
                    message="Invalid API key or expired access token",
                    status_code=response.status_code,
                )

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text}

                raise APIError(
                    message=error_data.get("message", f"API error: {response.status_code}"),
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response.json()

        except requests.RequestException as e:
            _logger.error(f"Request failed: {e}")
            raise APIError(message=f"Request failed: {str(e)}") from e

    def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
        speed: float = 1.25,
        audio_format: str = "mp3",
    ) -> SpeechSynthesisResponse:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize to speech.
            voice_id: ID of the voice to use for synthesis.
            audio_format: Audio format (mp3, wav, etc.).

        Returns:
            Speech synthesis response with audio data.

        Raises:
            ValidationError: If input parameters are invalid.
            APIError: If synthesis request fails.
        """
        if not text or not text.strip():
            raise ValidationError(message="Text input cannot be empty")
        if not voice_id or not voice_id.strip():
            raise ValidationError(message="Voice ID cannot be empty")

        request_data = SpeechSynthesisRequest(
            input_text=text,
            voice_id=voice_id,
            audio_format=audio_format,
        )

        response_data = self._make_request(
            method="POST",
            endpoint="/audio/speech",
            json_data=request_data.to_dict(),
        )

        _logger.info(f"Synthesized speech for voice: {voice_id}")
        return SpeechSynthesisResponse.from_dict(response_data)

    def list_voices(self) -> list[Voice]:
        """Get list of available voices.

        Returns:
            List of available voices.

        Raises:
            APIError: If request fails.
        """
        response_data = self._make_request(
            method="GET",
            endpoint="/voices",
        )

        voices = []
        # Handle both list and dict responses
        if isinstance(response_data, list):
            voice_list = response_data
        else:
            voice_list = response_data.get("voices", [])

        for voice_data in voice_list:
            voices.append(
                Voice(
                    voice_id=voice_data.get("id", voice_data.get("voice_id", "")),
                    name=voice_data.get("name", ""),
                    gender=voice_data.get("gender"),
                    language=voice_data.get("language"),
                )
            )

        _logger.info(f"Retrieved {len(voices)} available voices")
        return voices

    def get_voice(self, *, voice_id: str) -> Voice:
        """Get details for a specific voice.

        Args:
            voice_id: ID of the voice to retrieve.

        Returns:
            Voice details.

        Raises:
            ValidationError: If voice_id is invalid.
            APIError: If request fails.
        """
        if not voice_id or not voice_id.strip():
            raise ValidationError(message="Voice ID cannot be empty")

        response_data = self._make_request(
            method="GET",
            endpoint=f"/voices/{voice_id}",
        )

        _logger.info(f"Retrieved voice details: {voice_id}")
        return Voice(
            voice_id=response_data.get("id", response_data.get("voice_id")),
            name=response_data.get("name", ""),
            gender=response_data.get("gender"),
            language=response_data.get("language"),
        )

    def create_access_token(self) -> AccessToken:
        """Create an access token from API key.

        Returns:
            Access token response.

        Raises:
            APIError: If token creation fails.
        """
        response_data = self._make_request(
            method="POST",
            endpoint="/auth/token",
        )

        token = AccessToken.from_dict(response_data)
        self._access_token = token.access_token
        _logger.info("Created access token")
        return token

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()
        _logger.debug("Closed Speechify client session")

    def __enter__(self) -> "SpeechifyClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
