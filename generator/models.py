from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


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


@dataclass
class InstructorSection:
    title: str
    learning_objectives: List[str]
    talking_points: List[str]
    suggested_activities: List[str]
    estimated_time_minutes: Optional[int]


@dataclass
class InstructorGuide:
    sections: List[InstructorSection]


@dataclass
class VideoSegment:
    title: str
    narration: str
    screen_directions: str
    approx_duration_seconds: Optional[int]


@dataclass
class VideoScript:
    segments: List[VideoSegment]


@dataclass
class QuickRefStep:
    step_number: int
    title: str
    action: str
    notes: Optional[str]


@dataclass
class QuickReferenceGuide:
    steps: List[QuickRefStep]


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
