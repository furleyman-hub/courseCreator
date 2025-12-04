"""Placeholder LLM-like generators for course materials."""

from __future__ import annotations

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


def generate_class_outline(full_text: str, course_title: str, class_type: str) -> ClassOutline:
    """Return a mock class outline for the provided content.

    # TODO: integrate real LLM here
    """

    sections = [
        OutlineSection(
            title="Introduction and Objectives",
            objectives=["Set context", "Highlight key outcomes"],
            duration_minutes=10,
            subtopics=["Welcome", "Agenda", "Relevance to learners"],
        ),
        OutlineSection(
            title="Core Concepts",
            objectives=["Present fundamentals", "Connect concepts to use cases"],
            duration_minutes=35,
            subtopics=["Concept A", "Concept B", "Mini demo"],
        ),
        OutlineSection(
            title="Hands-on Practice",
            objectives=["Guide learners through steps", "Encourage experimentation"],
            duration_minutes=25,
            subtopics=["Guided exercise", "Reflection"],
        ),
    ]
    return ClassOutline(title=f"{course_title} ({class_type})", sections=sections)


def generate_instructor_guide(full_text: str, course_title: str, class_type: str) -> InstructorGuide:
    """Return a mock instructor guide.

    # TODO: integrate real LLM here
    """

    sections = [
        InstructorSection(
            title="Opening",
            learning_objectives=["Establish rapport", "Clarify expectations"],
            talking_points=["Share course purpose", "Ask about prior knowledge"],
            suggested_activities=["Icebreaker poll", "Pair introductions"],
            estimated_time_minutes=8,
        ),
        InstructorSection(
            title="Demonstration",
            learning_objectives=["Show the workflow", "Explain rationale"],
            talking_points=["Narrate each step", "Call out shortcuts"],
            suggested_activities=["Live demo", "Q&A"],
            estimated_time_minutes=20,
        ),
        InstructorSection(
            title="Wrap-up",
            learning_objectives=["Summarize learnings", "Preview next steps"],
            talking_points=["Recap key takeaways", "Provide resources"],
            suggested_activities=["Exit ticket", "Share links"],
            estimated_time_minutes=7,
        ),
    ]
    return InstructorGuide(sections=sections)


def generate_video_script(full_text: str, course_title: str, class_type: str) -> VideoScript:
    """Return a mock video script with screen directions.

    # TODO: integrate real LLM here
    """

    segments = [
        VideoSegment(
            title="Hook",
            narration=f"Welcome to {course_title}. Let's dive into why this matters.",
            screen_directions="Show course title slide; slow zoom-in on headline.",
            approx_duration_seconds=20,
        ),
        VideoSegment(
            title="Demo",
            narration="Watch as we perform the core task step by step.",
            screen_directions="Capture screen; cursor highlights key buttons; zoom on form fields.",
            approx_duration_seconds=60,
        ),
        VideoSegment(
            title="Summary",
            narration="Here are the top takeaways and where to learn more.",
            screen_directions="Return to slides; bullet points fade in; show resource links.",
            approx_duration_seconds=25,
        ),
    ]
    return VideoScript(segments=segments)


def generate_quick_reference(full_text: str, course_title: str, class_type: str) -> QuickReferenceGuide:
    """Return a mock quick reference guide.

    # TODO: integrate real LLM here
    """

    steps = [
        QuickRefStep(step_number=1, title="Prepare", action="Open the project workspace and verify access.", notes="Ensure login credentials are ready."),
        QuickRefStep(step_number=2, title="Configure", action="Adjust settings according to the template.", notes="Focus on defaults that impact performance."),
        QuickRefStep(step_number=3, title="Run", action="Execute the workflow and monitor outcomes.", notes="Capture screenshots of key results."),
    ]
    return QuickReferenceGuide(steps=steps)
