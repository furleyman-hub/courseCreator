"""Markdown exporters for generated training artifacts."""

from __future__ import annotations

from .models import ClassOutline, InstructorGuide, QuickReferenceGuide, VideoScript


def outline_to_markdown(outline: ClassOutline) -> str:
    lines = [f"# {outline.title}"]
    for section in outline.sections:
        lines.append(f"\n## {section.title}")
        if section.objectives:
            lines.append("**Objectives:**")
            for obj in section.objectives:
                lines.append(f"- {obj}")
        if section.subtopics:
            lines.append("**Subtopics:**")
            for topic in section.subtopics:
                lines.append(f"  - {topic}")
        if section.duration_minutes is not None:
            lines.append(f"**Duration:** {section.duration_minutes} minutes")
    return "\n".join(lines)


def instructor_guide_to_markdown(guide: InstructorGuide) -> str:
    lines = ["# Instructor Guide"]
    for section in guide.sections:
        lines.append(f"\n## {section.title}")
        if section.learning_objectives:
            lines.append("**Learning Objectives:**")
            for obj in section.learning_objectives:
                lines.append(f"- {obj}")
        if section.talking_points:
            lines.append("**Talking Points:**")
            for point in section.talking_points:
                lines.append(f"- {point}")
        if section.suggested_activities:
            lines.append("**Suggested Activities:**")
            for activity in section.suggested_activities:
                lines.append(f"- {activity}")
        if section.estimated_time_minutes is not None:
            lines.append(f"**Estimated Time:** {section.estimated_time_minutes} minutes")
    return "\n".join(lines)


def video_script_to_markdown(script: VideoScript) -> str:
    lines = ["# Video Script"]
    for idx, segment in enumerate(script.segments, start=1):
        lines.append(f"\n## Segment {idx}: {segment.title}")
        lines.append("**Narration:**")
        lines.append(segment.narration)
        lines.append("**Screen Directions:**")
        lines.append(segment.screen_directions)
        if segment.approx_duration_seconds is not None:
            lines.append(f"**Approx Duration:** {segment.approx_duration_seconds} seconds")
    return "\n".join(lines)


def quick_ref_to_markdown(qrg: QuickReferenceGuide) -> str:
    lines = ["# Quick Reference Guide"]
    for step in qrg.steps:
        lines.append(f"\n## Step {step.step_number}: {step.title}")
        lines.append(f"**Action:** {step.action}")
        if step.notes:
            lines.append(f"**Notes:** {step.notes}")
    return "\n".join(lines)
