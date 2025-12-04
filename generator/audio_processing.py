"""Audio transcription (STT) and narration synthesis (TTS) using OpenAI."""

from __future__ import annotations

import io
from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import get_client, TRANSCRIBE_MODEL, TTS_MODEL


# -------------------------------------------------------------------
# Speech-to-Text (audio transcription)
# -------------------------------------------------------------------

def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """
    Transcribe uploaded audio files using OpenAI's gpt-4o-transcribe model.
    Returns a combined transcript string.
    """

    if not audio_files:
        return ""

    client = get_client()
    all_transcripts = []

    for file in audio_files:
        try:
            audio_bytes = file.read()

            response = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=("audio_input", audio_bytes),
            )

            # The new STT API returns plain text in 'text'
            transcript = response.text or ""
            if not transcript:
                transcript = f"[No speech detected in {file.name}]"

            all_transcripts.append(f"--- Transcript from {file.name} ---\n{transcript}")

        except Exception as exc:
            all_transcripts.append(f"[Transcription failed for {file.name}: {exc}]")

    return "\n\n".join(all_transcripts).strip()


# -------------------------------------------------------------------
# Text-to-Speech (narration audio for video script)
# -------------------------------------------------------------------

def synthesize_narration_audio(video_script: VideoScript) -> Dict[str, bytes]:
    """
    Generate narration audio (wav byte strings) for each video script segment
    using OpenAI's gpt-4o-mini-tts model.

    Returns:
        { "filename.wav": audio_bytes }
    """

    client = get_client()
    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        narration_text = segment.narration.strip()

        if not narration_text:
            # Skip empty segments
            continue

        try:
            # Create TTS
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice="alloy",            # built-in high-quality voice
                input=narration_text,
                format="wav",
            )

            # In OpenAI SDK 2.x, audio bytes are in response.read()
            audio_bytes = response.read()

            filename = f"segment_{idx}.wav"
            audio_payloads[filename] = audio_bytes

        except Exception as exc:
            error_audio = f"Error generating TTS for segment {idx}: {exc}".encode("utf-8")
            audio_payloads[f"segment_{idx}_ERROR.txt"] = error_audio

    return audio_payloads
