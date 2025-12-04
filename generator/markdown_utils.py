from __future__ import annotations

from typing import List
from .models import (
    ClassOutline,
    InstructorGuide,
    VideoScript,
    QuickReferenceGuide,
)


def outline_to_markdown(outline: ClassOutline) -> str:
    """Convert a ClassOutline into markdown."""
    lines: List[str] = [f"# {outline.title}", ""]

    for section in outline.sections:
        lines.append(f"## {section.title}")
        if section.objectives:
            lines.append("### Objectives")
            for obj in section.objectives:
                lines.append(f"- {obj}")
            lines.append("")
        if section.subtopics:
            lines.append("### Subtopics")
            for topic in section.subtopics:
                lines.append(f"- {topic}")
            lines.append("")
        if section.duration_minutes:
            lines.append(f"**Duration:** {section.duration_minutes} minutes")
            lines.append("")

    return "\n".join(lines).strip()


def instructor_guide_to_markdown(guide: InstructorGuide) -> str:
    """Convert an InstructorGuide into markdown."""
    lines: List[str] = ["# Instructor Guide", ""]

    for section in guide.sections:
        lines.append(f"## {section.title}")
        if section.learning_objectives:
            lines.append("### Learning Objectives")
            for obj in section.learning_objectives:
                lines.append(f"- {obj}")
            lines.append("")
        if section.talking_points:
            lines.append("### Talking Points")
            for tp in section.talking_points:
                lines.append(f"- {tp}")
            lines.append("")
        if section.suggested_activities:
            lines.append("### Suggested Activities")
            for act in section.suggested_activities:
                lines.append(f"- {act}")
            lines.append("")
        if section.estimated_time_minutes:
            lines.append(f"**Estimated Time:** {section.estimated_time_minutes} minutes")
            lines.append("")

    return "\n".join(lines).strip()


def video_script_to_markdown(script: VideoScript) -> str:
    """Convert a VideoScript into markdown."""
    lines: List[str] = ["# Video Script", ""]

    for idx, segment in enumerate(script.segments, start=1):
        lines.append(f"## Segment {idx}: {segment.title}")
        lines.append("### Narration")
        lines.append(segment.narration)
        lines.append("")
        lines.append("### Screen Directions")
        lines.append(segment.screen_directions)
        lines.append("")
        if segment.approx_duration_seconds:
            lines.append(f"**Approx Duration:** {segment.approx_duration_seconds} seconds")
        lines.append("")

    return "\n".join(lines).strip()


def quick_ref_to_markdown(qrg: QuickReferenceGuide) -> str:
    """Convert a QuickReferenceGuide into markdown."""
    lines: List[str] = ["# Quick Reference Guide", ""]

    for step in qrg.steps:
        lines.append(f"## Step {step.step_number}: {step.title}")
        lines.append(f"**Action:** {step.action}")
        if step.notes:
            lines.append(f"**Notes:** {step.notes}")
        lines.append("")

    return "\n".join(lines).strip()
