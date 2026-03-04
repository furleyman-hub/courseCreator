"""Standalone TTS: parse a document into chunks and synthesize each one."""

from __future__ import annotations

import io
import struct
import wave
import zipfile
from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .gemini_client import (
    GEMINI_TTS_FLASH,
    MissingGeminiKeyError,
    VOICE_DISPLAY_TO_NAME,
    get_genai,
)


# -------------------------------------------------------------------
# Document → text chunks
# -------------------------------------------------------------------

def parse_document_to_chunks(uploaded_file: UploadedFile) -> List[str]:
    """
    Parse an uploaded .txt, .md, or .docx file into a list of text chunks.

    Chunks are separated by blank lines (double newline) for text/markdown files,
    and by blank paragraph objects for DOCX files.  Empty chunks are dropped.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".docx"):
        return _parse_docx(uploaded_file)

    # .txt or .md — read as UTF-8 text
    raw = uploaded_file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")

    return _split_by_blank_lines(text)


def _split_by_blank_lines(text: str) -> List[str]:
    """Split text on one-or-more blank lines, stripping each chunk."""
    import re
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split on blank lines (two or more consecutive newlines)
    raw_chunks = re.split(r"\n{2,}", text)
    return [c.strip() for c in raw_chunks if c.strip()]


def _parse_docx(uploaded_file: UploadedFile) -> List[str]:
    """Parse a DOCX file: blank paragraphs are separators; contiguous non-blank
    paragraphs are joined into a single chunk."""
    try:
        from docx import Document  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "python-docx is required to parse .docx files. "
            "Run: pip install python-docx"
        ) from exc

    doc = Document(io.BytesIO(uploaded_file.read()))
    chunks: List[str] = []
    current: List[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            current.append(text)
        else:
            if current:
                chunks.append("\n".join(current))
                current = []

    # Flush the last block
    if current:
        chunks.append("\n".join(current))

    return [c for c in chunks if c]


# -------------------------------------------------------------------
# Gemini TTS synthesis helpers
# -------------------------------------------------------------------

def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 24000, num_channels: int = 1,
                sample_width: int = 2) -> bytes:
    """Wrap raw PCM bytes in a WAV container and return as bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def _synthesize_one_chunk(
    genai,
    text: str,
    voice_name: str,
    model: str,
    style_prompt: str = "",
) -> bytes:
    """
    Call Gemini TTS for a single text chunk.
    Returns WAV bytes.
    """
    # Optional: prepend style instruction
    if style_prompt.strip():
        input_text = f"{style_prompt.strip()}\n\n{text}"
    else:
        input_text = text

    response = genai.models.generate_content(
        model=model,
        contents=input_text,
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

    # The audio data is in response.candidates[0].content.parts[0].inline_data.data
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    return _pcm_to_wav(audio_data)


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def synthesize_chunks(
    chunks: List[str],
    voice_display: str,
    model: str = GEMINI_TTS_FLASH,
    style_prompt: str = "",
) -> Dict[str, bytes]:
    """
    Synthesize a list of text chunks to audio using Gemini TTS.

    Parameters
    ----------
    chunks : list[str]
        Text segments to convert.
    voice_display : str
        Display name such as "Zephyr (Bright)". Looked up in VOICE_DISPLAY_TO_NAME.
    model : str
        Gemini TTS model name.
    style_prompt : str
        Optional natural-language style instruction prepended to each chunk.

    Returns
    -------
    dict[str, bytes]
        Mapping of filename → WAV bytes (or error .txt bytes on failure).
    """
    voice_name = VOICE_DISPLAY_TO_NAME.get(voice_display, "Zephyr")

    genai = get_genai()

    results: Dict[str, bytes] = {}
    for idx, chunk in enumerate(chunks, start=1):
        filename = f"chunk_{idx:03d}.wav"
        try:
            wav_bytes = _synthesize_one_chunk(
                genai, chunk, voice_name, model, style_prompt
            )
            results[filename] = wav_bytes
        except MissingGeminiKeyError:
            raise
        except Exception as exc:
            error_filename = f"chunk_{idx:03d}_ERROR.txt"
            results[error_filename] = (
                f"Error synthesizing chunk {idx}:\n{exc}\n\nText:\n{chunk}"
            ).encode("utf-8")

    return results


def chunks_to_zip(audio_dict: Dict[str, bytes]) -> bytes:
    """Package a {filename: bytes} dict into a ZIP archive and return the bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, data in audio_dict.items():
            zf.writestr(filename, data)
    return buf.getvalue()


__all__ = [
    "parse_document_to_chunks",
    "synthesize_chunks",
    "chunks_to_zip",
]
