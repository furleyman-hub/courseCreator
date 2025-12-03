import json
import os
from typing import Any, Dict, Optional

from openai import OpenAI

from backend.models.types import (
    ClassOutline,
    ClassOutlineSection,
    InstructorGuide,
    InstructorGuideSection,
    QuickReferenceGuide,
    QuickReferenceStep,
    VideoScript,
    VideoScriptSegment,
)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _get_client(api_key: Optional[str]) -> Optional[OpenAI]:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def _structured_completion(system_prompt: str, user_prompt: str, api_key: Optional[str]) -> Optional[Dict[str, Any]]:
    client = _get_client(api_key)
    if not client:
        return None

    try:
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=0.35,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception:
        # Fail soft and allow fallback templates
        return None


def _outline_fallback(course_title: str) -> ClassOutline:
    sections = [
        ClassOutlineSection(
            title="Introduction",
            objectives=["Understand goals", "Set expectations"],
            durationMinutes=10,
        ),
        ClassOutlineSection(
            title="Core Concepts",
            objectives=["Learn the basics", "Review examples"],
            durationMinutes=30,
        ),
    ]
    return ClassOutline(title=course_title, sections=sections)


def _instructor_fallback(course_title: str) -> InstructorGuide:
    sections = [
        InstructorGuideSection(
            title="Kickoff",
            learningObjectives=["Establish rapport", "Preview agenda"],
            talkingPoints=["Welcome participants", "Share outcomes"],
            suggestedActivities=["Icebreaker question"],
            timingMinutes=5,
        ),
        InstructorGuideSection(
            title="Hands-on Walkthrough",
            learningObjectives=["Practice workflow"],
            talkingPoints=["Demonstrate key steps", "Highlight pitfalls"],
            suggestedActivities=["Live demo", "Group exercise"],
            timingMinutes=25,
        ),
    ]
    return InstructorGuide(courseTitle=course_title, sections=sections)


def _video_fallback(course_title: str) -> VideoScript:
    segments = [
        VideoScriptSegment(
            title="Scene 1 - Overview",
            narration="Welcome to the training. In this lesson, we'll cover the essentials.",
            screenDirections="Show title slide, slow zoom, then fade to dashboard.",
            durationSeconds=45,
        ),
        VideoScriptSegment(
            title="Scene 2 - Doing the Work",
            narration="Click on 'Create' to start a new project and fill in the details.",
            screenDirections="Capture cursor clicking Create, highlight form fields, zoom on Save button.",
            durationSeconds=75,
        ),
    ]
    return VideoScript(courseTitle=course_title, segments=segments)


def _qrg_fallback(course_title: str) -> QuickReferenceGuide:
    steps = [
        QuickReferenceStep(
            stepNumber=1,
            title="Set Up",
            action="Open the application and sign in with your credentials.",
            notes="Use SSO when available.",
        ),
        QuickReferenceStep(
            stepNumber=2,
            title="Create Item",
            action="Click 'Create', enter required fields, and press Save.",
            notes="Fields marked * are mandatory.",
        ),
    ]
    return QuickReferenceGuide(courseTitle=course_title, steps=steps)


def generate_class_outline(
    text: str, course_title: str, class_type: str, api_key: Optional[str] = None
) -> ClassOutline:
    system = """You are an instructional designer creating a concise, structured class outline.
Return JSON with keys: title (string) and sections (list of {title, objectives [strings], durationMinutes number})."""
    user = (
        f"Course title: {course_title}\n"
        f"Class type: {class_type}\n"
        f"Source text:\n{text}"
    )

    parsed = _structured_completion(system, user, api_key)
    if parsed:
        try:
            return ClassOutline.parse_obj(parsed)
        except Exception:
            pass
    return _outline_fallback(course_title)


def generate_instructor_guide(
    text: str, course_title: str, class_type: str, api_key: Optional[str] = None
) -> InstructorGuide:
    system = """You are creating an instructor guide. Return JSON with keys: courseTitle, sections (list of {title, learningObjectives [strings], talkingPoints [strings], suggestedActivities [strings], timingMinutes number})."""
    user = (
        f"Course title: {course_title}\n"
        f"Class type: {class_type}\n"
        f"Source text:\n{text}"
    )

    parsed = _structured_completion(system, user, api_key)
    if parsed:
        try:
            return InstructorGuide.parse_obj(parsed)
        except Exception:
            pass
    return _instructor_fallback(course_title)


def generate_video_script(
    text: str, course_title: str, class_type: str, api_key: Optional[str] = None
) -> VideoScript:
    system = """You are writing a training video script. Return JSON with keys: courseTitle, segments (list of {title, narration, screenDirections, durationSeconds number})."""
    user = (
        f"Course title: {course_title}\n"
        f"Class type: {class_type}\n"
        f"Source text:\n{text}"
    )

    parsed = _structured_completion(system, user, api_key)
    if parsed:
        try:
            return VideoScript.parse_obj(parsed)
        except Exception:
            pass
    return _video_fallback(course_title)


def generate_quick_reference(
    text: str, course_title: str, class_type: str, api_key: Optional[str] = None
) -> QuickReferenceGuide:
    system = """You are drafting a concise quick reference guide. Return JSON with keys: courseTitle, steps (list of {stepNumber, title, action, notes})."""
    user = (
        f"Course title: {course_title}\n"
        f"Class type: {class_type}\n"
        f"Source text:\n{text}"
    )

    parsed = _structured_completion(system, user, api_key)
    if parsed:
        try:
            return QuickReferenceGuide.parse_obj(parsed)
        except Exception:
            pass
    return _qrg_fallback(course_title)
