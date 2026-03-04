"""Standalone TTS: parse a document into chunks and synthesize each one."""

from __future__ import annotations

import io
import zipfile
from typing import Dict, List

from streamlit.runtime.uploaded_file_manager import UploadedFile

from .openai_client import (
    TTS_MODEL,
    MissingOpenAIKeyError,
    get_client,
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
# OpenAI TTS synthesis helpers
# -------------------------------------------------------------------

def _synthesize_one_chunk(
    client,
    text: str,
    voice: str,
    model: str,
    style_prompt: str = "",
) -> bytes:
    """
    Call OpenAI TTS for a single text chunk.
    Returns MP3 bytes directly (no PCM conversion needed).
    """
    kwargs: dict = dict(model=model, voice=voice, input=text, response_format="mp3")
    # gpt-4o-mini-tts supports an optional style instructions parameter
    if style_prompt.strip() and model == TTS_MODEL:
        kwargs["instructions"] = style_prompt.strip()
    response = client.audio.speech.create(**kwargs)
    return response.content


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def synthesize_chunks(
    chunks: List[str],
    voice_display: str,
    model: str = TTS_MODEL,
    style_prompt: str = "",
) -> Dict[str, bytes]:
    """
    Synthesize a list of text chunks to MP3 using OpenAI TTS.

    Parameters
    ----------
    chunks : list[str]
        Text segments to convert.
    voice_display : str
        OpenAI voice name (e.g. "nova", "alloy").
    model : str
        OpenAI TTS model. gpt-4o-mini-tts supports style instructions;
        tts-1-hd gives highest audio quality.
    style_prompt : str
        Optional speaking-style instruction (gpt-4o-mini-tts only).

    Returns
    -------
    dict[str, bytes]
        Mapping of filename → MP3 bytes (or error .txt bytes on failure).
    """
    client = get_client()

    results: Dict[str, bytes] = {}
    for idx, chunk in enumerate(chunks, start=1):
        filename = f"chunk_{idx:03d}.mp3"
        try:
            mp3_bytes = _synthesize_one_chunk(
                client, chunk, voice_display, model, style_prompt
            )
            results[filename] = mp3_bytes
        except MissingOpenAIKeyError:
            raise
        except Exception as exc:
            error_filename = f"chunk_{idx:03d}_ERROR.txt"
            results[error_filename] = (
                f"Error synthesizing chunk {idx}:\n{exc}\n\nChunk text:\n{chunk}"
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
