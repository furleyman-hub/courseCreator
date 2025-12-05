from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ------------------------------------------------------
# Class Outline
# ------------------------------------------------------

@dataclass
class OutlineSection:
    title: str
    objectives: List[str]
    duration_minutes: Optional[int]
    subtopics: List[str]


@dataclass
class ClassOutline:
    title: str
    sections: List[OutlineSection]


# ------------------------------------------------------
# Instructor Guide
# ------------------------------------------------------

@dataclass
class InstructorSection:
    """
    One topic in the Instructional Framework.

    Example:
      title: "Managing Linked Workbooks in Excel"
      learning_objectives: [...]
      instructional_steps: [...]
      key_points: [...]
      estimated_time_minutes: 10
    """
    title: str
    learning_objectives: List[str]
    instructional_steps: List[str]
    key_points: List[str]
    estimated_time_minutes: Optional[int]


@dataclass
class InstructorGuide:
    """
    Whole design document for the session:
      - Front matter (training plan, target audience, etc.)
      - Instructional framework topics in `sections`
    """

    # Front-matter / overview
    training_plan_and_goals: str = ""
    target_audience: str = ""
    prerequisites: str = ""
    office365_status: str = ""
    learning_objectives: List[str] = field(default_factory=list)

    # Preparation & setup
    required_materials_and_equipment: List[str] = field(default_factory=list)
    instructor_setup: List[str] = field(default_factory=list)
    participant_setup: List[str] = field(default_factory=list)
    handouts: List[str] = field(default_factory=list)

    # Class meta
    class_type: str = ""
    class_checklist_before: List[str] = field(default_factory=list)
    class_checklist_start: List[str] = field(default_factory=list)
    class_checklist_after: List[str] = field(default_factory=list)

    # Instructional framework topics
    sections: List[InstructorSection] = field(default_factory=list)


# ------------------------------------------------------
# Video Script
# ------------------------------------------------------

@dataclass
class VideoSegment:
    title: str
    narration: str
    screen_directions: str
    approx_duration_seconds: Optional[int]


@dataclass
class VideoScript:
    segments: List[VideoSegment]


# ------------------------------------------------------
# Quick Reference Guide
# ------------------------------------------------------

@dataclass
class QuickRefStep:
    step_number: int
    title: str
    action: str
    notes: Optional[str]


@dataclass
class QuickReferenceGuide:
    steps: List[QuickRefStep]


# ------------------------------------------------------
# Combined Package Used by app.py
# ------------------------------------------------------

@dataclass
class GeneratedPackage:
    outline: ClassOutline
    instructor_guide: InstructorGuide
    video_script: VideoScript
    quick_reference: QuickReferenceGuide


__all__ = [
    "ClassOutline",
    "OutlineSection",
    "InstructorGuide",
    "InstructorSection",
    "VideoScript",
    "VideoSegment",
    "QuickReferenceGuide",
    "QuickRefStep",
    "GeneratedPackage",
]
