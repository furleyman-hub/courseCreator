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
    if not full_text:
        return "[No source text supplied; rely on general instructional design best practices.]"
    return shorten(full_text, width=limit, placeholder="... [truncated]")


def _call_json_response(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
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
        return json.loads(response.output_text)

    except MissingOpenAIKeyError:
        raise

    except (APIError, APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, NotFoundError) as exc:
        st.error(f"OpenAI API error: {exc}")
        raise

    except Exception as exc:
        st.error(f"Unexpected error calling OpenAI: {exc}")
        raise


# ------------------------------------------------------
# Parsers
# ------------------------------------------------------

def _parse_outline(payload: Dict[str, Any], course_title: str, class_type: str) -> ClassOutline:
    sections_data = payload.get("sections", [])
    sections: List[OutlineSection] = []

    for item in sections_data:
        try:
            sections.append(
                OutlineSection(
                    title=item.get("title", "Untitled Section"),
                    objectives=item.get("objectives", []) or [],
                    duration_minutes=item.get("duration_minutes"),
                    subtopics=item.get("subtopics", []) or [],
                )
            )
        except Exception:
            continue

    title = payload.get("title") or f"{course_title} ({class_type})"
    return ClassOutline(title=title, sections=sections)


def _parse_instructor_guide(payload: Dict[str, Any]) -> InstructorGuide:
    sections_data = payload.get("sections", [])
    sections: List[InstructorSection] = []

    for item in sections_data:
        try:
            sections.append(
                InstructorSection(
                    title=item.get("title", "Untitled Section"),
                    learning_objectives=item.get("learning_objectives", []) or [],
                    talking_points=item.get("talking_points", []) or [],
                    suggested_activities=item.get("suggested_activities", []) or [],
                    estimated_time_minutes=item.get("estimated_time_minutes"),
                )
            )
        except Exception:
            continue

    return InstructorGuide(sections=sections)


def _parse_video_script(payload: Dict[str, Any]) -> VideoScript:
    segments_data = payload.get("segments", [])
    segments: List[VideoSegment] = []

    for item in segments_data:
        try:
            segments.append(
                VideoSegment(
                    title=item.get("title", "Untitled Segment"),
                    narration=item.get("narration", ""),
                    screen_directions=item.get("screen_directions", ""),
                    approx_duration_seconds=item.get("approx_duration_seconds"),
                )
            )
        except Exception:
            continue

    return VideoScript(segments=segments)


def _parse_quick_reference(payload: Dict[str, Any]) -> QuickReferenceGuide:
    steps_data = payload.get("steps", [])
    steps: List[QuickRefStep] = []

    for item in steps_data:
        try:
            steps.append(
                QuickRefStep(
                    step_number=item.get("step_number"),
                    title=item.get("title", "Step"),
                    action=item.get("action", ""),
                    notes=item.get("notes"),
                )
            )
        except Exception:
            continue

    return QuickReferenceGuide(steps=steps)


# ------------------------------------------------------
# MAIN LLM GENERATION FUNCTIONS (FIXED WITH STRICT JSON PROMPTS)
# ------------------------------------------------------

def generate_class_outline(full_text: str, course_title: str, class_type: str) -> ClassOutline:
    excerpt = _format_source_excerpt(full_text)

    system_prompt = """
You are an expert instructional designer.
Return ONLY valid JSON matching EXACTLY this structure:

{
  "title": "string",
  "sections": [
    {
      "title": "string",
      "objectives": ["string"],
      "duration_minutes": 30,
      "subtopics": ["string"]
    }
  ]
}

No markdown. No commentary. JSON only.
""".strip()

    user_prompt = f"""
Course title: {course_title}
Class type: {class_type}

Build a structured class outline using this source text:
{excerpt}
""".strip()

    try:
        payload = _call_json_response(system_prompt, user_prompt)
        return _parse_outline(payload, course_title, class_type)

    except MissingOpenAIKeyError as exc:
        st.error(str(exc))

    except Exception:
        st.error("Class outline generation failed.")

    return ClassOutline(title=f"{course_ti_
