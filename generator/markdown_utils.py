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
    lines: List[str] = ["# Instructor Guide", ""]

    # Training plan and goals
    if guide.training_plan_and_goals:
        lines.append("## Training plan and goals")
        lines.append(guide.training_plan_and_goals.strip())
        lines.append("")

    # Target audience
    if guide.target_audience:
        lines.append("## Target audience")
        lines.append(guide.target_audience.strip())
        lines.append("")

    # Prerequisites
    if guide.prerequisites:
        lines.append("## Prerequisites")
        lines.append(guide.prerequisites.strip())
        lines.append("")

    # Office 365 status
    if guide.office365_status:
        lines.append("## Office 365 status")
        lines.append(guide.office365_status.strip())
        lines.append("")

    # Session learning objectives
    if guide.learning_objectives:
        lines.append("## Learning objectives")
        lines.append("By the end of the session, participants will be able to:")
        lines.append("")
        for obj in guide.learning_objectives:
            lines.append(f"1. {obj}")
        lines.append("")

    # Preparation & course setup
    if (
        guide.required_materials_and_equipment
        or guide.instructor_setup
        or guide.participant_setup
        or guide.handouts
    ):
        lines.append("## Preparation and course setup")

        if guide.required_materials_and_equipment:
            lines.append("### Required materials and equipment")
            for item in guide.required_materials_and_equipment:
                lines.append(f"- {item}")
            lines.append("")

        if guide.instructor_setup:
            lines.append("### Setup – instructor")
            for item in guide.instructor_setup:
                lines.append(f"- {item}")
            lines.append("")

        if guide.participant_setup:
            lines.append("### Setup – participants")
            for item in guide.participant_setup:
                lines.append(f"- {item}")
            lines.append("")

        if guide.handouts:
            lines.append("### Handouts (optional)")
            for item in guide.handouts:
                lines.append(f"- {item}")
            lines.append("")

    # Type of class
    if guide.class_type:
        lines.append("## Type of class")
        lines.append(guide.class_type.strip())
        lines.append("")

    # Class checklist
    if (
        guide.class_checklist_before
        or guide.class_checklist_start
        or guide.class_checklist_after
    ):
        lines.append("## Class checklist")

        if guide.class_checklist_before:
            lines.append("**Before class:**")
            for item in guide.class_checklist_before:
                lines.append(f"- {item}")
            lines.append("")

        if guide.class_checklist_start:
            lines.append("**Start of class:**")
            for item in guide.class_checklist_start:
                lines.append(f"- {item}")
            lines.append("")

        if guide.class_checklist_after:
            lines.append("**After class:**")
            for item in guide.class_checklist_after:
                lines.append(f"- {item}")
            lines.append("")

    # Instructional framework topics
    if guide.sections:
        lines.append("## Instructional framework")
        lines.append("")
        for section in guide.sections:
            lines.append(f"### Topic: {section.title}")

            if section.estimated_time_minutes:
                lines.append(f"**Estimated Time:** {section.estimated_time_minutes} minutes")
                lines.append("")

            if section.learning_objectives:
                lines.append("**Learning Objectives**")
                for obj in section.learning_objectives:
                    lines.append(f"- {obj}")
                lines.append("")

            if section.instructional_steps:
                lines.append("**Instructional Steps:**")
                for step in section.instructional_steps:
                    lines.append(f"- {step}")
                lines.append("")

            if section.key_points:
                lines.append("**Key Points:**")
                for kp in section.key_points:
                    lines.append(f"- {kp}")
                lines.append("")

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
