from __future__ import annotations

import io
import wave
from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import get_client, TRANSCRIBE_MODEL
from .gemini_client import (
    GEMINI_TTS_FLASH,
    MissingGeminiKeyError,
    VOICE_DISPLAY_TO_NAME,
    get_genai,
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
# WAV encoding helper
# -------------------------------------------------------------------

def _pcm_to_wav(
    pcm_bytes: bytes,
    sample_rate: int = 24000,
    num_channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    """Wrap raw 16-bit PCM bytes in a WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


# -------------------------------------------------------------------
# TTS synthesis (now uses Google Gemini)
# -------------------------------------------------------------------

def synthesize_narration_audio(
    video_script: VideoScript,
    voice_display: str = "Zephyr (Bright)",
    model: str = GEMINI_TTS_FLASH,
) -> Dict[str, bytes]:
    """
    Generate one TTS WAV file per video script segment using Gemini TTS.

    Parameters
    ----------
    video_script : VideoScript
        The generated video script whose narration segments will be synthesized.
    voice_display : str
        Display name like "Zephyr (Bright)".  Maps to the Gemini prebuilt voice name.
    model : str
        Gemini TTS model identifier (Flash or Pro).

    Returns
    -------
    dict[str, bytes]
        {filename: wav_bytes} — or error text bytes if a segment fails.
    """
    voice_name = VOICE_DISPLAY_TO_NAME.get(voice_display, "Zephyr")

    genai = get_genai()
    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        narration = (segment.narration or "").strip()
        if not narration:
            continue

        filename = f"segment_{idx}.wav"

        try:
            response = genai.models.generate_content(
                model=model,
                contents=narration,
                config=genai.types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=genai.types.SpeechConfig(
                        voice_config=genai.types.VoiceConfig(
                            prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        )
                    ),
                ),
            )

            pcm_bytes = response.candidates[0].content.parts[0].inline_data.data
            audio_payloads[filename] = _pcm_to_wav(pcm_bytes)

        except MissingGeminiKeyError:
            raise
        except Exception as exc:
            error_msg = f"Error generating TTS for segment {idx}: {exc}"
            audio_payloads[f"{filename}_ERROR.txt"] = error_msg.encode("utf-8")

    return audio_payloads
