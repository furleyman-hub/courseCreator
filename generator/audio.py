from __future__ import annotations

from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import get_client, TRANSCRIBE_MODEL, TTS_MODEL


def transcribe_audio_files(audio_files: List[UploadedFile]) -> str:
    """Very simple transcription example (still OK to be stubbed if you want)."""
    if not audio_files:
        return ""

    client = get_client()
    transcripts: List[str] = []

    for f in audio_files:
        try:
            # Upload the in-memory file directly
            transcript = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=(f.name, f.read()),  # (filename, bytes)
            )
            transcripts.append(f"[{f.name}]\n{transcript.text}")
        except Exception as exc:
            transcripts.append(f"[{f.name}] TRANSCRIPTION ERROR: {exc}")

    return "\n\n".join(transcripts)


def synthesize_narration_audio(video_script: VideoScript) -> Dict[str, bytes]:
    """Generate one TTS file per segment using OpenAI audio.speech."""

    client = get_client()
    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        narration = (segment.narration or "").strip()
        if not narration:
            # Nothing to synthesize for this segment
            continue

        filename = f"segment_{idx}.wav"

        try:
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice="alloy",
                input=narration,
                # ✅ correct keyword in the new SDK
                response_format="wav",
            )

            # The response is a binary stream-like object; read() gives us the bytes
            audio_bytes: bytes = response.read()
            audio_payloads[filename] = audio_bytes

        except Exception as exc:
            # If anything goes wrong, we still return a useful error file
            error_msg = f"Error generating TTS for segment {idx}: {exc}"
            audio_payloads[f"{filename}_ERROR.txt"] = error_msg.encode("utf-8")

    return audio_payloads
