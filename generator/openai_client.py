"""OpenAI client helpers and shared model constants."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from openai import OpenAI


class MissingOpenAIKeyError(Exception):
    """Raised when no OpenAI API key is configured."""


# -------------------------------------------------------------------
# Model constants (compatible with OpenAI responses + JSON mode)
# -------------------------------------------------------------------

TEXT_MODEL = "gpt-4.1"             # used for outline, guide, script, QRG
TRANSCRIBE_MODEL = "gpt-4o-transcribe"   # STT
TTS_MODEL = "gpt-4o-mini-tts"     # TTS — supports style instructions + all voices
TTS_MODEL_HD = "tts-1-hd"         # TTS — highest audio quality

# Voices supported by ALL models (tts-1, tts-1-hd, gpt-4o-mini-tts)
OPENAI_TTS_VOICES_HD_COMPATIBLE: list[str] = [
    "alloy", "ash", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer",
]

# Additional voices only available on gpt-4o-mini-tts
OPENAI_TTS_VOICES_MINI_ONLY: list[str] = ["ballad", "cedar", "marin", "verse"]

# Full voice list for gpt-4o-mini-tts (recommended: marin, cedar for highest quality)
OPENAI_TTS_VOICES: list[str] = OPENAI_TTS_VOICES_HD_COMPATIBLE + OPENAI_TTS_VOICES_MINI_ONLY


# -------------------------------------------------------------------
# API key loader
# -------------------------------------------------------------------

def _read_api_key() -> Optional[str]:
    """
    Resolve the OpenAI API key from Streamlit secrets or environment.
    Streamlit Cloud uses st.secrets automatically.
    """

    # Streamlit secrets (preferred in Cloud)
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return str(st.secrets["OPENAI_API_KEY"])
    except (FileNotFoundError, Exception):
        pass

    # Local environment
    return os.environ.get("OPENAI_API_KEY")


# -------------------------------------------------------------------
# Client factory
# -------------------------------------------------------------------

def get_client() -> OpenAI:
    """Return a configured OpenAI client or raise if the key is missing."""
    api_key = _read_api_key()

    if not api_key:
        raise MissingOpenAIKeyError(
            "OpenAI API key not found. Please set st.secrets['OPENAI_API_KEY'] "
            "or define the OPENAI_API_KEY environment variable."
        )

    return OpenAI(api_key=api_key)


__all__ = [
    "MissingOpenAIKeyError",
    "TEXT_MODEL",
    "TRANSCRIBE_MODEL",
    "TTS_MODEL",
    "TTS_MODEL_HD",
    "OPENAI_TTS_VOICES",
    "OPENAI_TTS_VOICES_HD_COMPATIBLE",
    "OPENAI_TTS_VOICES_MINI_ONLY",
    "get_client",
]
