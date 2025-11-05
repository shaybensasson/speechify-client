"""Exception classes for Speechify REST client."""

from typing import Any


class SpeechifyError(Exception):
    """Base exception for Speechify client errors."""

    def __init__(
        self,
        *,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize Speechify error.

        Args:
            message: Error message.
            status_code: HTTP status code from the API response.
            response_data: Full response data from the API.
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class AuthenticationError(SpeechifyError):
    """Raised when authentication fails."""

    pass


class APIError(SpeechifyError):
    """Raised when API request fails."""

    pass


class ValidationError(SpeechifyError):
    """Raised when input validation fails."""

    pass
