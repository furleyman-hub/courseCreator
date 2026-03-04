from __future__ import annotations

from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import (
    get_client,
    TRANSCRIBE_MODEL,
    TTS_MODEL,
    TTS_MODEL_HD,
    OPENAI_TTS_VOICES_HD_COMPATIBLE,
    MissingOpenAIKeyError,
)


# -------------------------------------------------------------------
# Audio transcription (still uses OpenAI Whisper – unchanged)
# -------------------------------------------------------------------

def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """Transcribe a list of audio files using OpenAI Whisper."""
    if not audio_files:
        return ""

    client = get_client()
    transcripts: List[str] = []

    for f in audio_files:
        try:
            transcript = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=(f.name, f.read()),
            )
            transcripts.append(f"[{f.name}]\n{transcript.text}")
        except Exception as exc:
            transcripts.append(f"[{f.name}] TRANSCRIPTION ERROR: {exc}")

    return "\n\n".join(transcripts)


# -------------------------------------------------------------------
# TTS synthesis (OpenAI)
# -------------------------------------------------------------------

def synthesize_narration_audio(
    video_script: VideoScript,
    voice_display: str = "nova",
    model: str = TTS_MODEL,
) -> Dict[str, bytes]:
    """
    Generate one MP3 file per video script segment using OpenAI TTS.

    Parameters
    ----------
    video_script : VideoScript
        The generated video script whose narration segments will be synthesized.
    voice_display : str
        OpenAI voice name (e.g. "nova", "alloy").
    model : str
        OpenAI TTS model identifier.

    Returns
    -------
    dict[str, bytes]
        {filename: mp3_bytes} — or error text bytes if a segment fails.
    """
    client = get_client()
    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        narration = (segment.narration or "").strip()
        if not narration:
            continue

        filename = f"segment_{idx}.mp3"
        try:
            effective_model = model
            # Upgrade to gpt-4o-mini-tts if the chosen voice isn't HD-compatible
            if model == TTS_MODEL_HD and voice_display not in OPENAI_TTS_VOICES_HD_COMPATIBLE:
                effective_model = TTS_MODEL
            response = client.audio.speech.create(
                model=effective_model,
                voice=voice_display,
                input=narration,
                response_format="mp3",
            )
            audio_payloads[filename] = response.read()
        except MissingOpenAIKeyError:
            raise
        except Exception as exc:
            error_key = f"segment_{idx}_ERROR.txt"
            audio_payloads[error_key] = (
                f"Error generating TTS for segment {idx}: {exc}"
            ).encode("utf-8")

    return audio_payloads
