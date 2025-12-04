"""OpenAI-powered content generation for training materials."""

from __future__ import annotations

import json
from textwrap import shorten
from typing import Any, Dict, List

import streamlit as st

# Correct OpenAI exceptions for SDK 2.x
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


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _format_source_excerpt(full_text: str, limit: int = 6000) -> str:
    """Shorten source text to keep prompts efficient."""
    if not full_text:
        return "[No source text available.]"
    return shorten(full_text, width=limit, placeholder="... [truncated]")


def _call_json_response(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Generic wrapper for a JSON-only Responses API call.
    Ensures we always return a Python dict.
    """
    client = get_client()

    try:
        response = client.responses.create(
            model=TEXT_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        # Responses API helper for JSON text
        return json.loads(response.output_text)

    except MissingOpenAIKeyError:
        raise

    except (APIError, APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, NotFoundError) as exc:
        st.error(f"OpenAI API error: {exc}")
        raise

    except Exception as exc:
        st.error(f"Unexpected OpenAI error: {exc}")
        raise


# -------------------------------------------------------------------
# Parsing helpers
# -------------------------------------------------------------------

def _parse_outline(payload: Dict[str, Any], course_title: str, class_type: str) -> ClassOutline:
    sections_data = payload.get("sections", []) if isinstance(payload, dict) else []
    sections: List[OutlineSection] = []

    for item in sections_data:
        try:
            sections.append(
                OutlineSection(
                    title=str(item.get("title", "Untitled Section")),
                    objectives=list(item.get("objectives", []) or []),
                    duration_minutes=item.get("duration_minutes"),
                    subtopics=list(item.get("subtopics", []) or []),
                )
            )
        except Exception:
            continue

    title = payload.get("title") if isinstance(payload, dict) else None
    return ClassOutline(
        title=title or f"{course_title} ({class_type})",
        sections=sections,
    )


def _parse_instructor_guide(payload: Dict[str, Any]) -> InstructorGuide:
    sections_data = payload.get("sections", []) if isinstance(payload, dict) else []
    sections: List[InstructorSection] = []

    for item in sections_data:
        try:
            sections.append(
                InstructorSection(
                    title=str(item.get("title", "Untitled Section")),
                    learning_objectives=list(item.get("learning_objectives", []) or []),
                    talking_points=list(item.get("talking_points", []) or []),
                    suggested_activities=list(item.get("suggested_activities", []) or []),
                    estimated_time_minutes=item.get("estimated_time_minutes"),
                )
            )
        except Exception:
            continue

    return InstructorGuide(sections=sections)


def _parse_video_script(payload: Dict[str, Any]) -> VideoScript:
    segments_data = payload.get("segments", []) if isinstance(payload, dict) else []
    segments: List[VideoSegment] = []

    for item in segments_data:
        try:
            segments.append(
                VideoSegment(
                    title=str(item.get("title", "Untitled Segment")),
                    narration=str(item.get("narration", "")),
                    screen_directions=str(item.get("screen_directions", "")),
                    approx_duration_seconds=item.get("approx_duration_seconds"),
                )
            )
        except Exception:
            continue

    return VideoScript(segments=segments)


def _parse_quick_reference(payload: Dict[str, Any]) -> QuickReferenceGuide:
    steps_data = payload.get("steps", []) if isinstance(payload, dict) else []
    steps: List[QuickRefStep] = []

    for item in steps_data:
        try:
            steps.append(
                QuickRefStep(
                    step_number=int(item.get("step_number", len(steps) + 1)),
                    title=str(item.get("title", "Step")),
                    action=str(item.get("action", "")),
                    notes=item.get("notes"),
                )
            )
        except Exception:
            continue

    return QuickReferenceGuide(steps=steps)


# -------------------------------------------------------------------
# Main generator wrappers
# -------------------------------------------------------------------

def generate_class_outline(full_text: str, course_title: str, class_type: str) -> ClassOutline:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You are an instructional designer who produces clear, structured, actionable class outlines. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Create a ClassOutline JSON object for the course '{course_title}' ({class_type}).\n"
        f"Use the following source text as guidance:\n{excerpt}\n\n"
        "Schema: {title: str, sections: [ {title, objectives: list[str], duration_minutes: int|null, subtopics: list[str]} ]}"
    )

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_outline(payload, course_title, class_type)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Class outline generation failed.")

    return ClassOutline(title=f"{course_title} ({class_type})", sections=[])


def generate_instructor_guide(full_text: str, course_title: str, class_type: str) -> InstructorGuide:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You create detailed instructor guides that include learning objectives, talking points, activities, and time estimates. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Produce an InstructorGuide JSON for '{course_title}' ({class_type}).\n"
        f"Use this source text:\n{excerpt}\n\n"
        "Schema: {sections: [ {title, learning_objectives, talking_points, suggested_activities, estimated_time_minutes} ]}"
    )

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_instructor_guide(payload)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Instructor guide generation failed.")

    return InstructorGuide(sections=[])


def generate_video_script(full_text: str, course_title: str, class_type: str) -> VideoScript:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You write high-quality training video scripts with narration and precise screen directions. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Draft a VideoScript JSON for '{course_title}' ({class_type}).\n"
        f"Use this source text for context:\n{excerpt}\n\n"
        "Schema: {segments: [ {title, narration, screen_directions, approx_duration_seconds} ]}"
    )

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_video_script(payload)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Video script generation failed.")

    return VideoScript(segments=[])


def generate_quick_reference(full_text: str, course_title: str, class_type: str) -> QuickReferenceGuide:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You create concise, numbered quick reference guides (QRGs) with clear action steps. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Produce a QuickReferenceGuide JSON for '{course_title}' ({class_type}).\n"
        f"Use this source text:\n{excerpt}\n\n"
        "Schema: {steps: [ {step_number, title, action, notes} ]}"
    )

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_quick_reference(payload)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Quick reference generation failed.")

    return QuickReferenceGuide(steps=[])


__all__ = [
    "generate_class_outline",
    "generate_instructor_guide",
    "generate_quick_reference",
    "generate_video_script",
]
