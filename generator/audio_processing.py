"""Real audio transcription and TTS synthesis using the OpenAI audio APIs."""

from __future__ import annotations

import io
from typing import Dict, List

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import get_client, TRANSCRIBE_MODEL, TTS_MODEL, MissingOpenAIKeyError


# ---------------------------------------------------------
# STT (Speech-to-Text)
# ---------------------------------------------------------

def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """Transcribe uploaded audio files using OpenAI's audio transcription API.
    
    Returns a combined transcript string.
    """

    if not audio_files:
        return ""

    client = get_client()
    transcripts: List[str] = []

    for file in audio_files:
        try:
            audio_bytes = file.read()
            audio_stream = io.BytesIO(audio_bytes)

            result = client.audio.transcriptions.create(
                file=audio_stream,
                model=TRANSCRIBE_MODEL,
            )

            transcripts.append(f"[{file]()
