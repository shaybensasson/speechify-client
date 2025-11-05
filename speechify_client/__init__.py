"""Speechify REST client for text-to-speech synthesis.

This module provides a simple, type-safe REST client for the Speechify AI API,
enabling easy integration of text-to-speech capabilities into Python applications.
"""

from speechify_client.client import SpeechifyClient
from speechify_client.exceptions import SpeechifyError

__all__ = ["SpeechifyClient", "SpeechifyError"]
__version__ = "0.1.0"
