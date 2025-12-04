"""Utilities for converting generated training materials to Markdown."""

from __future__ import annotations
from typing import List

from .models import (
    ClassOutline,
    InstructorGuide,
    VideoScript,
    QuickReferenceGuide,
)


# -------------------------------------------------------------------
# Outline → Markdown
# -------------------------------------------------------------------

def outline_to_markdown(outline: ClassOutline) -> str:
    md = [f"# {outline.title}", ""]
    for section in outline.sections:
        md.append(f"## {section.title}")

        if section.objectives:
            md.append("**Objectives:**")
            for obj in section.objectives:
                md.append(f"- {obj}")
            md.append("")

        if section.subtopics:
            md.append("**Subtopics:**")
            for sub in section.subtopics:
                md.append(f"- {sub}")
            md.append("")

        if section.duration_minutes:
            md.append(f"**Estimated Time:** {section.duration_minutes} minutes")
            md.append("")

    return "\n".join(md).strip()


# -------------------------------------------------------------------
# Instructor Guide → Markdown
# -------------------------------------------------------------------

def instructor_guide_to_markdown(guide: InstructorGuide) -> str:
    md: List[str] = ["# Instructor Guide", ""]

    for section in guide.sections:
        md.append(f"## {section.title}")

        if section.learning_objectives:
            md.append("**Learning Objectives:**")
            for item in section.learning_objectives:
                md.append(f"- {item}")
            md.append("")

        if section.talking_points:
            md.append("**Talking Points:**")
            for tp in section.talking_points:
                md.append(f"- {tp}")
            md.append("")

        if section.suggested_activities:
            md.append("**Activities / Demonstrations:**")
            for act in section.suggested_activities:
                md.append(f"- {act}")
            md.append("")

        if section.estimated_time_minutes:
            md.append(f"**Estimated Time:** {section.estimated_time_minutes} minutes")
            md.append("")

    return "\n".join(md).strip()


# -------------------------------------------------------------------
# Video Script → Markdown
# -------------------------------------------------------------------

def video_script_to_markdown(script: VideoScript) -> str:
    md = ["# Video Script", ""]

    for seg in script.segments:
        md.append(f"## {seg.title}")

        if seg.narration:
            md.append("**Narration:**")
            md.append(seg.narration)
            md.append("")

        if seg.screen_directions:
            md.append("**Screen Directions:**")
            md.append(seg.screen_directions)
            md.append("")

        if seg.approx_duration_seconds:
            md.append(f"**Approx Duration:** {seg.approx_duration_seconds} seconds")
            md.append("")

    return "\n".join(md).strip()


# -------------------------------------------------------------------
# Quick Reference Guide → Markdown
# -------------------------------------------------------------------

def qref_to_markdown(qref: QuickReferenceGuide) -> str:
    md = ["# Quick Reference Guide", ""]

    for step in qref.steps:
        md.append(f"## Step {step.step_number}: {step.title}")
        md.append(step.action)

        if step.notes:
            md.append("")
            md.append(f"**Notes:** {step.notes}")

        md.append("")

    return "\n".join(md).strip()


# -------------------------------------------------------------------
# Export
# -------------------------------------------------------------------

__all__ = [
    "outline_to_markdown",
    "instructor_guide_to_markdown",
    "video_script_to_markdown",
    "qref_to_markdown",
]
