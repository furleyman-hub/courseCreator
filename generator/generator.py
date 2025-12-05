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
        raise

    except (APIError, APIConnectionError, RateLimitError,
            AuthenticationError, BadRequestError, NotFoundError) as exc:
        st.error(f"OpenAI API error: {exc}")
        raise

    except Exception as exc:
        st.error(f"Unexpected OpenAI error: {exc}")
        raise


# ------------------------------------------------------
# Parsing helpers
# ------------------------------------------------------

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
    if not isinstance(payload, dict):
        return InstructorGuide()

    # Sections = Instructional Framework topics
    sections_data = payload.get("sections", []) or []
    sections: List[InstructorSection] = []

    for item in sections_data:
        try:
            sections.append(
                InstructorSection(
                    title=str(item.get("title", "Untitled Topic")),
                    learning_objectives=list(item.get("learning_objectives", []) or []),
                    instructional_steps=list(item.get("instructional_steps", []) or []),
                    key_points=list(item.get("key_points", []) or []),
                    estimated_time_minutes=item.get("estimated_time_minutes"),
                )
            )
        except Exception:
            continue

    guide = InstructorGuide(sections=sections)

    # Front-matter / overview
    guide.training_plan_and_goals = str(payload.get("training_plan_and_goals", "") or "")
    guide.target_audience = str(payload.get("target_audience", "") or "")
    guide.prerequisites = str(payload.get("prerequisites", "") or "")
    guide.office365_status = str(payload.get("office365_status", "") or "")
    guide.learning_objectives = list(payload.get("learning_objectives", []) or [])

    # Preparation & setup
    guide.required_materials_and_equipment = list(
        payload.get("required_materials_and_equipment", []) or []
    )
    guide.instructor_setup = list(payload.get("instructor_setup", []) or [])
    guide.participant_setup = list(payload.get("participant_setup", []) or [])
    guide.handouts = list(payload.get("handouts", []) or [])

    # Class meta
    guide.class_type = str(payload.get("class_type", "") or "")
    guide.class_checklist_before = list(payload.get("class_checklist_before", []) or [])
    guide.class_checklist_start = list(payload.get("class_checklist_start", []) or [])
    guide.class_checklist_after = list(payload.get("class_checklist_after", []) or [])

    return guide



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


# ------------------------------------------------------
# Main LLM Functions
# ------------------------------------------------------

def generate_class_outline(full_text: str, course_title: str, class_type: str) -> ClassOutline:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You are an instructional designer who produces concise, actionable class outlines. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Create a ClassOutline JSON object for the course '{course_title}' ({class_type}).\n"
        f"Source text:\n{excerpt}\n\n"
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
        "You create detailed instructor design documents for live attorney training sessions. "
        "Use the exact JSON schema provided. The front matter should match the structure of a "
        "professional design document (training plan, audience, prerequisites, setup, checklists), "
        "and 'sections' should represent the Instructional Framework topics. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Produce an InstructorGuide JSON for '{course_title}' ({class_type}).\n"
        f"Base it on this source text; be specific and concrete, and use Excel/legal context where present.\n"
        f"Source:\n{excerpt}\n\n"
        "Schema (use these exact property names):\n"
        "{\n"
        '  \"training_plan_and_goals\": str,\n'
        '  \"target_audience\": str,\n'
        '  \"prerequisites\": str,\n'
        '  \"office365_status\": str,\n'
        '  \"learning_objectives\": [str],\n'
        '  \"required_materials_and_equipment\": [str],\n'
        '  \"instructor_setup\": [str],\n'
        '  \"participant_setup\": [str],\n'
        '  \"handouts\": [str],\n'
        '  \"class_type\": str,\n'
        '  \"class_checklist_before\": [str],\n'
        '  \"class_checklist_start\": [str],\n'
        '  \"class_checklist_after\": [str],\n'
        '  \"sections\": [\n'
        "    {\n"
        '      \"title\": str,\n'
        '      \"estimated_time_minutes\": int | null,\n'
        '      \"learning_objectives\": [str],\n'
        '      \"instructional_steps\": [str],\n'
        '      \"key_points\": [str]\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_instructor_guide(payload)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Instructor guide generation failed.")

    return InstructorGuide()


def generate_video_script(full_text: str, course_title: str, class_type: str) -> VideoScript:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = (
        "You write video scripts with narration and precise screen directions. Always reply with JSON only."
    )

    user_prompt = (
        f"Draft a VideoScript JSON for '{course_title}' ({class_type}).\n"
        f"Source text:\n{excerpt}\n\n"
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
        "You create succinct quick reference guides with numbered steps and optional notes. "
        "Always reply with JSON only."
    )

    user_prompt = (
        f"Produce a QuickReferenceGuide JSON for '{course_title}' ({class_type}).\n"
        f"Source text:\n{excerpt}\n\n"
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
