"""Audio processing helpers using OpenAI for transcription and TTS."""
from __future__ import annotations

import os
import tempfile
from typing import Dict, List

import streamlit as st
from openai import OpenAIError
from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import MissingOpenAIKeyError, TTS_MODEL, TRANSCRIBE_MODEL, get_client


def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """Transcribe uploaded audio files using the OpenAI STT API."""

    if not audio_files:
        return ""

    transcripts: List[str] = []
    try:
        client = get_client()
    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
        return ""

    for file in audio_files:
        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[-1]) as tmp:
                tmp.write(file.getbuffer())
                tmp_path = tmp.name

            with open(tmp_path, "rb") as audio_handle:
                response = client.audio.transcriptions.create(model=TRANSCRIBE_MODEL, file=audio_handle)
                transcripts.append(response.text)
        except (OpenAIError, OSError) as exc:
            st.error(f"Transcription failed for {file.name}: {exc}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    return "\n".join(filter(None, transcripts))


def synthesize_narration_audio(video_script: VideoScript) -> Dict[str, bytes]:
    """Generate narration audio for each video segment using OpenAI TTS."""

    payloads: Dict[str, bytes] = {}
    try:
        client = get_client()
    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
        return payloads

    for idx, segment in enumerate(video_script.segments, start=1):
        safe_title = segment.title.replace(" ", "_").lower() or f"segment_{idx}"
        filename = f"segment_{idx:02d}_{safe_title}.mp3"
        try:
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice="alloy",
                input=segment.narration or segment.title,
            )
            audio_bytes = response.read()
            payloads[filename] = audio_bytes
        except OpenAIError as exc:
            st.error(f"TTS failed for segment '{segment.title}': {exc}")
    return payloads
