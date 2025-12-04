"""OpenAI client helpers and shared model constants."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from openai import OpenAI


class MissingOpenAIKeyError(Exception):
    """Raised when no OpenAI API key is configured."""


# Recommended stable models
TEXT_MODEL = "gpt-4.1"                # supports JSON structured responses
TRANSCRIBE_MODEL = "gpt-4o-transcribe"   # correct transcription model
TTS_MODEL = "gpt-4o-mini-tts"            # correct TTS model


def _read_api_key() -> Optional[str]:
    """Resolve an OpenAI API key from Streamlit secrets or the environment."""

    if "OPENAI_API_KEY" in st.secrets:
        return str(st.secrets["OPENAI_API_KEY"])

    return os.environ.get("OPENAI_API_KEY")


def get_client() -> OpenAI:
    """Return a configured OpenAI client or raise if the key is missing."""

    api_key = _read_api_key()
    if not api_key:
        raise MissingOpenAIKeyError(
            "OpenAI API key not found. Set st.secrets['OPENAI_API_KEY'] or the OPENAI_API_KEY environment variable."
        )

    return OpenAI(api_key=api_key)


__all__ = [
    "MissingOpenAIKeyError",
    "TEXT_MODEL",
    "TRANSCRIBE_MODEL",
    "TTS_MODEL",
    "get_client",
]
