"""Standalone TTS: parse a document into text chunks and synthesize each to MP3."""

from __future__ import annotations

import io
import re
import zipfile
from typing import Dict, List

from openai import OpenAI

from .openai_client import get_client, TTS_MODEL, TTS_MODEL_HD, OPENAI_TTS_VOICES_HD_COMPATIBLE


# ---------------------------------------------------------------------------
# Document parsing
# ---------------------------------------------------------------------------

def parse_document_to_chunks(uploaded_file) -> List[str]:
    """Parse an uploaded .txt, .md, or .docx file into non-empty text chunks.

    Text/Markdown: split on blank lines.
    DOCX: blank paragraphs act as separators; adjacent non-blank paragraphs are
          joined into a single chunk.
    """
    name = uploaded_file.name.lower()

    if name.endswith(".docx"):
        return _parse_docx(uploaded_file)

    raw = uploaded_file.read()
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return _split_blank_lines(text)


def _split_blank_lines(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [c.strip() for c in re.split(r"\n{2,}", text) if c.strip()]


def _parse_docx(uploaded_file) -> List[str]:
    from docx import Document  # type: ignore
    doc = Document(io.BytesIO(uploaded_file.read()))
    chunks, current = [], []
    for para in doc.paragraphs:
        line = para.text.strip()
        if line:
            current.append(line)
        elif current:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks


# ---------------------------------------------------------------------------
# OpenAI TTS synthesis
# ---------------------------------------------------------------------------

def _call_tts(client: OpenAI, text: str, voice: str, model: str,
              style: str = "") -> bytes:
    """Make a single OpenAI TTS call and return raw MP3 bytes."""
    # tts-1-hd does not support voices that only exist on gpt-4o-mini-tts
    if model == TTS_MODEL_HD and voice not in OPENAI_TTS_VOICES_HD_COMPATIBLE:
        model = TTS_MODEL

    params: dict = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": "mp3",
    }
    # speaking-style instructions are only supported by gpt-4o-mini-tts
    if style.strip() and model == TTS_MODEL:
        params["instructions"] = style.strip()

    response = client.audio.speech.create(**params)
    # .read() returns the complete response body as bytes
    return response.read()


def synthesize_chunks(
    chunks: List[str],
    voice_display: str,
    model: str = TTS_MODEL,
    style_prompt: str = "",
) -> Dict[str, bytes]:
    """Synthesize a list of text chunks to MP3 files using OpenAI TTS.

    Returns a dict mapping filename → bytes.
    On per-chunk failure the entry is named ``chunk_NNN_ERROR.txt`` and
    its value is the UTF-8-encoded error message.
    """
    client = get_client()
    results: Dict[str, bytes] = {}

    for i, chunk in enumerate(chunks, start=1):
        try:
            mp3 = _call_tts(client, chunk, voice_display, model, style_prompt)
            results[f"chunk_{i:03d}.mp3"] = mp3
        except Exception as exc:
            results[f"chunk_{i:03d}_ERROR.txt"] = (
                f"TTS error on chunk {i}:\n{exc}\n\nText:\n{chunk}"
            ).encode("utf-8")

    return results


def chunks_to_zip(audio_dict: Dict[str, bytes]) -> bytes:
    """Pack a ``{filename: bytes}`` mapping into an in-memory ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in audio_dict.items():
            zf.writestr(name, data)
    return buf.getvalue()


__all__ = ["parse_document_to_chunks", "synthesize_chunks", "chunks_to_zip"]
