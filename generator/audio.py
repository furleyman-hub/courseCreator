from __future__ import annotations

import base64
import time
from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .models import VideoScript
from .openai_client import get_client, TRANSCRIBE_MODEL
from .gemini_client import (
    GEMINI_TTS_FLASH,
    MissingGeminiKeyError,
    VOICE_DISPLAY_TO_NAME,
    get_gemini_client,
)
from google.genai import types


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
# MP3 encoding helper
# -------------------------------------------------------------------

def _pcm_to_mp3(
    pcm_bytes: bytes,
    sample_rate: int = 24000,
    num_channels: int = 1,
    bit_rate: int = 128,
) -> bytes:
    """
    Encode raw 16-bit little-endian PCM bytes to MP3 using lameenc.
    Gemini TTS returns Linear16 PCM; this wraps it in a browser-playable MP3.
    """
    try:
        import lameenc  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "lameenc is required for MP3 encoding. Run: pip install lameenc"
        ) from exc

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bit_rate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(num_channels)
    encoder.set_quality(2)  # 2 = highest quality

    mp3_data = encoder.encode(pcm_bytes)
    mp3_data += encoder.flush()
    return mp3_data


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

    client = get_gemini_client()
    audio_payloads: Dict[str, bytes] = {}

    for idx, segment in enumerate(video_script.segments, start=1):
        narration = (segment.narration or "").strip()
        if not narration:
            continue

        filename = f"segment_{idx}.mp3"

        last_exc: Exception = RuntimeError(f"TTS failed for segment {idx}")
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=narration,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_name,
                                )
                            )
                        ),
                    ),
                )

                # Some google-genai SDK versions return base64-encoded bytes rather
                # than decoded binary; decode defensively and fall back to raw bytes.
                raw = response.candidates[0].content.parts[0].inline_data.data
                try:
                    pcm_bytes = base64.b64decode(raw, validate=True)
                except Exception:
                    pcm_bytes = raw  # already raw PCM bytes
                audio_payloads[filename] = _pcm_to_mp3(pcm_bytes)
                break  # success

            except MissingGeminiKeyError:
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)  # 1s, 2s before retries 2 and 3
        else:
            error_key = f"segment_{idx}_ERROR.txt"
            error_msg = f"Error generating TTS for segment {idx}: {last_exc}"
            audio_payloads[error_key] = error_msg.encode("utf-8")

    return audio_payloads
