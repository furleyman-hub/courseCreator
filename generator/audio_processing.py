"""Stubbed audio processing helpers."""

from __future__ import annotations

from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript


def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """Return placeholder transcript text for uploaded audio files.

    This function is intentionally stubbed. In a real implementation, you could
    call Whisper or another speech-to-text provider here and aggregate the
    transcripts before returning them.
    """

    if not audio_files:
        return ""

    file_names = [file.name for file in audio_files]
    return "Transcribed audio from: " + ", ".join(file_names)


def synthesize_narration_audio(video_script: VideoScript) -> Dict[str, bytes]:
    """Return placeholder audio bytes keyed by filename for each script segment.

    In production, this is where you would call a TTS provider (e.g., OpenAI
    TTS or another service) to turn narration text into downloadable audio
    files.
    """

    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        filename = f"segment_{idx}.wav"
        # This is just a stub; replace with real audio synthesis output.
        audio_payloads[filename] = f"Fake audio for {segment.title}".encode("utf-8")

    return audio_payloads
