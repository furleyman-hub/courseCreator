"""OpenAI client helpers and shared model constants."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from openai import OpenAI


class MissingOpenAIKeyError(Exception):
    """Raised when no OpenAI API key is configured."""


TEXT_MODEL = "gpt-4.1-mini"
TRANSCRIBE_MODEL = "gpt-4o-transcribe"
TTS_MODEL = "gpt-4o-mini-tts"


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


def create_json_response(system_prompt: str, user_prompt: str, model: str = TEXT_MODEL) -> str:
    """Call the Responses API and return the JSON text payload."""

    client = get_client()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    return response.output_text


def transcribe_audio(file_handle, model: str = TRANSCRIBE_MODEL) -> str:
    """Transcribe audio using OpenAI STT."""

    client = get_client()
    response = client.audio.transcriptions.create(model=model, file=file_handle)
    return response.text


def synthesize_speech(input_text: str, model: str = TTS_MODEL, voice: str = "alloy") -> bytes:
    """Create speech audio for the provided text."""

    client = get_client()
    response = client.audio.speech.create(model=model, voice=voice, input=input_text)
    return response.read()


__all__ = [
    "MissingOpenAIKeyError",
    "TEXT_MODEL",
    "TRANSCRIBE_MODEL",
    "TTS_MODEL",
    "get_client",
    "create_json_response",
    "transcribe_audio",
    "synthesize_speech",
]
