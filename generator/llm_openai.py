"""OpenAI-powered content generation for training materials."""

from __future__ import annotations

import json
from textwrap import shorten
from typing import Any, Dict, List

import streamlit as st
from openai import OpenAIError

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
from .openai_client import (
    MissingOpenAIKeyError,
    TEXT_MODEL,
    create_json_response,
)


def _format_source_excerpt(full_text: str, limit: int = 6000) -> str:
    if not full_text:
        return "[No source text supplied; rely on general instructional design best practices.]"
    return shorten(full_text, width=limit, placeholder="... [truncated]")


def _call_json_response(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    response_text = create_json_response(system_prompt, user_prompt, model=TEXT_MODEL)
    return json.loads(response_text)


def _handle_errors(context: str, exc: Exception):
    if isinstance(exc, MissingOpenAIKeyError):
        st.error(str(exc))
    else:
        st.error(f"{context}: {exc}")


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
    return ClassOutline(title=title or f"{course_title} ({class_type})", sections=sections)


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


def generate_class_outline(full_text: str, course_title: str, class_type: str) -> ClassOutline:
    excerpt = _format_source_excerpt(full_text)
    system_prompt = (
        "You are an instructional designer who produces concise, actionable class outlines. "
        "Return a JSON object with keys: title (str), sections (list of objects with title, objectives list[str], "
        "duration_minutes int|null, subtopics list[str]). No additional keys."
    )
    user_prompt = (
        f"Create a ClassOutline JSON object for the course title '{course_title}' (type: {class_type}).\n"
        f"Use the following source material as guidance, focusing on key themes and logical flow.\n"
        f"Source excerpt:\n{excerpt}"
    )
    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_outline(payload, course_title, class_type)
    except (MissingOpenAIKeyError, OpenAIError, json.JSONDecodeError) as exc:
        _handle_errors("Unable to generate class outline", exc)
    except Exception as exc:  # pragma: no cover - defensive
        _handle_errors("Unexpected error while generating class outline", exc)
    return ClassOutline(title=f"{course_title} ({class_type})", sections=[])


def generate_instructor_guide(full_text: str, course_title: str, class_type: str) -> InstructorGuide:
    excerpt = _format_source_excerpt(full_text)
    system_prompt = (
        "You create detailed instructor guides with objectives, talking points, activities, and timing. "
        "Return a JSON object with key 'sections' as a list of objects containing: title (str), learning_objectives "
        "(list[str]), talking_points (list[str]), suggested_activities (list[str]), estimated_time_minutes (int|null)."
    )
    user_prompt = (
        f"Produce an InstructorGuide JSON object for the course '{course_title}' ({class_type}).\n"
        f"Base it on this source excerpt; prioritize clarity and actionable guidance.\n{excerpt}"
    )
    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_instructor_guide(payload)
    except (MissingOpenAIKeyError, OpenAIError, json.JSONDecodeError) as exc:
        _handle_errors("Unable to generate instructor guide", exc)
    except Exception as exc:  # pragma: no cover - defensive
        _handle_errors("Unexpected error while generating instructor guide", exc)
    return InstructorGuide(sections=[])


def generate_video_script(full_text: str, course_title: str, class_type: str) -> VideoScript:
    excerpt = _format_source_excerpt(full_text)
    system_prompt = (
        "You write video scripts with narration and precise screen directions. Return JSON with key 'segments' "
        "as a list of objects: title (str), narration (str), screen_directions (str), approx_duration_seconds (int|null)."
    )
    user_prompt = (
        f"Draft a VideoScript JSON for '{course_title}' ({class_type}). Include segments with narration, screen_directions, and approx_duration_seconds.\n"
        f"Source excerpt for context:\n{excerpt}"
    )
    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_video_script(payload)
    except (MissingOpenAIKeyError, OpenAIError, json.JSONDecodeError) as exc:
        _handle_errors("Unable to generate video script", exc)
    except Exception as exc:  # pragma: no cover - defensive
        _handle_errors("Unexpected error while generating video script", exc)
    return VideoScript(segments=[])


def generate_quick_reference(full_text: str, course_title: str, class_type: str) -> QuickReferenceGuide:
    excerpt = _format_source_excerpt(full_text)
    system_prompt = (
        "You create succinct quick reference guides with numbered steps and optional notes. Return JSON with key 'steps' "
        "as a list of objects: step_number (int), title (str), action (str), notes (str|null)."
    )
    user_prompt = (
        f"Produce a QuickReferenceGuide JSON for '{course_title}' ({class_type}). Steps should be numbered and concise.\n"
        f"Use this source excerpt for context:\n{excerpt}"
    )
    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_quick_reference(payload)
    except (MissingOpenAIKeyError, OpenAIError, json.JSONDecodeError) as exc:
        _handle_errors("Unable to generate quick reference guide", exc)
    except Exception as exc:  # pragma: no cover - defensive
        _handle_errors("Unexpected error while generating quick reference guide", exc)
    return QuickReferenceGuide(steps=[])


__all__ = [
    "generate_class_outline",
    "generate_instructor_guide",
    "generate_quick_reference",
    "generate_video_script",
]
