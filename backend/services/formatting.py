from typing import Dict, List

from backend.models.types import (
    ClassOutline,
    InstructorGuide,
    QuickReferenceGuide,
    VideoScript,
)


def outline_to_md(outline: ClassOutline) -> str:
    lines: List[str] = [f"# {outline.title}"]
    for section in outline.sections:
        lines.append(f"## {section.title}")
        if section.objectives:
            lines.append("**Objectives**")
            lines.extend(f"- {obj}" for obj in section.objectives)
        if section.durationMinutes:
            lines.append(f"_Duration: {section.durationMinutes} minutes_")
    return "\n\n".join(lines)


def instructor_to_md(guide: InstructorGuide) -> str:
    lines: List[str] = [f"# Instructor Guide: {guide.courseTitle}"]
    for section in guide.sections:
        lines.append(f"## {section.title}")
        for label, entries in (
            ("Learning Objectives", section.learningObjectives),
            ("Talking Points", section.talkingPoints),
            ("Suggested Activities", section.suggestedActivities),
        ):
            if entries:
                lines.append(f"**{label}**")
                lines.extend(f"- {entry}" for entry in entries)
        if section.timingMinutes:
            lines.append(f"_Timing: {section.timingMinutes} minutes_")
    return "\n\n".join(lines)


def video_to_md(video: VideoScript) -> str:
    lines: List[str] = [f"# Video Script: {video.courseTitle}"]
    for segment in video.segments:
        lines.append(f"## {segment.title}")
        if segment.narration:
            lines.append("**Narration**")
            lines.append(segment.narration)
        if segment.screenDirections:
            lines.append("**Screen Directions**")
            lines.append(segment.screenDirections)
        if segment.durationSeconds:
            lines.append(f"_Duration: {segment.durationSeconds} seconds_")
    return "\n\n".join(lines)


def qrg_to_md(qrg: QuickReferenceGuide) -> str:
    lines: List[str] = [f"# Quick Reference Guide: {qrg.courseTitle}"]
    for step in qrg.steps:
        lines.append(f"## Step {step.stepNumber}: {step.title}")
        if step.action:
            lines.append(f"- **Action:** {step.action}")
        if step.notes:
            lines.append(f"- **Notes:** {step.notes}")
    return "\n\n".join(lines)


def artifacts_to_md(payload: Dict[str, object]) -> Dict[str, str]:
    return {
        "outline": outline_to_md(payload["classOutline"]),
        "instructor": instructor_to_md(payload["instructorGuide"]),
        "video": video_to_md(payload["videoScript"]),
        "qrg": qrg_to_md(payload["quickReferenceGuide"]),
    }
