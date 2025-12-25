"""Noma - Surgical telemedicine platform.

This package provides real-time surgical visualization and automated
medical transcription capabilities.
"""

__version__ = "0.1.0"

from noma.api import create_app
from noma.config import get_config

__all__ = ["create_app", "get_config", "__version__"]
