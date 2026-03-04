"""Google Gemini client helpers and model constants for TTS."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st


class MissingGeminiKeyError(Exception):
    """Raised when no Gemini API key is configured."""


# -------------------------------------------------------------------
# Model constants
# -------------------------------------------------------------------

GEMINI_TTS_FLASH = "gemini-2.5-flash-preview-tts"
GEMINI_TTS_PRO = "gemini-2.5-pro-preview-tts"

# -------------------------------------------------------------------
# All 28 prebuilt voices – (voice_name, style_label)
# Used to populate UI selectors.
# -------------------------------------------------------------------

GEMINI_VOICES: list[tuple[str, str]] = [
    ("Zephyr", "Bright"),
    ("Puck", "Upbeat"),
    ("Charon", "Informative"),
    ("Kore", "Firm"),
    ("Fenrir", "Excitable"),
    ("Leda", "Youthful"),
    ("Orus", "Firm"),
    ("Aoede", "Breezy"),
    ("Callirhoe", "Easy-going"),
    ("Autonoe", "Bright"),
    ("Enceladus", "Breathy"),
    ("Iapetus", "Clear"),
    ("Umbriel", "Easy-going"),
    ("Algieba", "Smooth"),
    ("Despina", "Smooth"),
    ("Erinome", "Clear"),
    ("Algenib", "Gravelly"),
    ("Rasalgethi", "Informative"),
    ("Laomedeia", "Upbeat"),
    ("Achernar", "Soft"),
    ("Alnilam", "Firm"),
    ("Schedar", "Even"),
    ("Gacrux", "Mature"),
    ("Pulcherrima", "Forward"),
    ("Achird", "Friendly"),
    ("Zubenelgenubi", "Casual"),
    ("Vindemiatrix", "Gentle"),
    ("Sadachbia", "Lively"),
]

# Flat list of display strings, e.g. "Zephyr (Bright)"
VOICE_DISPLAY_NAMES: list[str] = [
    f"{name} ({style})" for name, style in GEMINI_VOICES
]

# Map display string → raw voice name
VOICE_DISPLAY_TO_NAME: dict[str, str] = {
    f"{name} ({style})": name for name, style in GEMINI_VOICES
}


# -------------------------------------------------------------------
# API key loader
# -------------------------------------------------------------------

def _read_api_key() -> Optional[str]:
    """
    Resolve the Gemini API key from Streamlit secrets or environment.
    """
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"])
    except (FileNotFoundError, Exception):
        pass

    return os.environ.get("GEMINI_API_KEY")


# -------------------------------------------------------------------
# Configured genai client (lazy-loaded so import errors surface clearly)
# -------------------------------------------------------------------

def get_gemini_client():
    """Import google-genai and return a configured Client, raising clearly if unavailable."""
    try:
        from google import genai  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. "
            "Run: pip install google-genai>=0.2.0"
        ) from exc

    api_key = _read_api_key()
    if not api_key:
        raise MissingGeminiKeyError(
            "Gemini API key not found. Please set st.secrets['GEMINI_API_KEY'] "
            "or the GEMINI_API_KEY environment variable."
        )

    return genai.Client(api_key=api_key)


__all__ = [
    "MissingGeminiKeyError",
    "GEMINI_TTS_FLASH",
    "GEMINI_TTS_PRO",
    "GEMINI_VOICES",
    "VOICE_DISPLAY_NAMES",
    "VOICE_DISPLAY_TO_NAME",
    "get_gemini_client",
]
