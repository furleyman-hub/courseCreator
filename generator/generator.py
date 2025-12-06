"""OpenAI-powered content generation for training materials."""

from __future__ import annotations

import json
from textwrap import shorten
from typing import Any, Dict, List

import streamlit as st

from openai import (
    APIError,
    APIConnectionError,
    BadRequestError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

from .models import (
    ClassOutline,
    InstructorGuide,
    InstructorSection,
    OutlineSection,
    QuickRefStep,
    QuickReferenceGuide,
    VideoScript,
    VideoSegment,
)
from .openai_client import MissingOpenAIKeyError, TEXT_MODEL, get_client


# ------------------------------------------------------
# Helpers
# ------------------------------------------------------


def _format_source_excerpt(full_text: str, limit: int = 6000) -> str:
    """Shortened excerpt of full text to keep prompts manageable."""
    if not full_text:
        return "[No source text supplied; rely on general instructional design best practices.]"
    return shorten(full_text, width=limit, placeholder="... [truncated]")


def _build_combined_source_text(full_text: str) -> str:
    """
    Combine the main source text with optional handwritten notes
    stored in Streamlit session_state under 'handwritten_notes_text'.

    This lets handwritten notes (OCR from images) act as instructor
    intent/context without changing any function signatures.
    """
    base_text = (full_text or "").strip()

    try:
        notes = (st.session_state.get("handwritten_notes_text", "") or "").strip()
    except Exception:
        notes = ""

    if notes:
        if base_text:
            return (
                base_text
                + "\n\n=== Additional notes from instructor (handwritten) ===\n"
                + notes
            )
        else:
            return (
                "=== Additional notes from instructor (handwritten) ===\n"
                + notes
            )

    return base_text


def _call_json_response(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """Call Chat Completions API in JSON mode and return parsed JSON."""
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        json_text = response.choices[0].message.content
        return json.loads(json_text)

    except MissingOpenAIKeyError:
        # Let caller handle missing key specifically if they want
        ra
