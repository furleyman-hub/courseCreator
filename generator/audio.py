"""Audio helpers: transcription (Whisper) and TTS narration (OpenAI TTS)."""

from __future__ import annotations

from typing import Dict, List

from openai import OpenAI

from .models import VideoScript
from .openai_client import (
    get_client,
    MissingOpenAIKeyError,
    TRANSCRIBE_MODEL,
    TTS_MODEL,
    TTS_MODEL_HD,
    OPENAI_TTS_VOICES_HD_COMPATIBLE,
)


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------

def transcribe_audio_files(audio_files: list) -> str:
    """Transcribe a list of uploaded audio files using OpenAI Whisper."""
    if not audio_files:
        return ""

    client = get_client()
    transcripts: List[str] = []

    for f in audio_files:
        try:
            result = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=(f.name, f.read()),
            )
            transcripts.append(f"[{f.name}]\n{result.text}")
        except Exception as exc:
            transcripts.append(f"[{f.name}] TRANSCRIPTION ERROR: {exc}")

    return "\n\n".join(transcripts)


# ---------------------------------------------------------------------------
# TTS narration
# ---------------------------------------------------------------------------

def synthesize_narration_audio(
    video_script: VideoScript,
    voice_display: str = "nova",
    model: str = TTS_MODEL,
) -> Dict[str, bytes]:
    """Generate one MP3 per video-script segment using OpenAI TTS.

    Returns ``{filename: mp3_bytes}``.  If a segment fails, the entry is
    named ``segment_N_ERROR.txt`` and contains the error message.
    """
    client = get_client()
    results: Dict[str, bytes] = {}

    for i, segment in enumerate(video_script.segments, start=1):
        text = (segment.narration or "").strip()
        if not text:
            continue

        filename = f"segment_{i}.mp3"
        try:
            # Some voices only exist on gpt-4o-mini-tts; upgrade automatically
            effective_model = model
            if model == TTS_MODEL_HD and voice_display not in OPENAI_TTS_VOICES_HD_COMPATIBLE:
                effective_model = TTS_MODEL

            response = client.audio.speech.create(
                model=effective_model,
                voice=voice_display,
                input=text,
                response_format="mp3",
            )
            results[filename] = response.read()

        except MissingOpenAIKeyError:
            raise
        except Exception as exc:
            results[f"segment_{i}_ERROR.txt"] = (
                f"TTS error for segment {i}: {exc}"
            ).encode("utf-8")

    return results
