"""Utilities for generating training class materials."""

from .models import (
    ClassOutline,
    GeneratedPackage,
    InstructorGuide,
    InstructorSection,
    OutlineSection,
    QuickRefStep,
    QuickReferenceGuide,
    VideoScript,
    VideoSegment,
)
from .audio_processing import synthesize_narration_audio, transcribe_audio_files
from .file_processing import extract_text_from_files
from .llm_openai import (
    generate_class_outline,
    generate_instructor_guide,
    generate_quick_reference,
    generate_video_script,
)
from .markdown_export import (
    instructor_guide_to_markdown,
    outline_to_markdown,
    quick_ref_to_markdown,
    video_script_to_markdown,
)

__all__ = [
    "ClassOutline",
    "GeneratedPackage",
    "InstructorGuide",
    "InstructorSection",
    "OutlineSection",
    "QuickRefStep",
    "QuickReferenceGuide",
    "VideoScript",
    "VideoSegment",
    "synthesize_narration_audio",
    "transcribe_audio_files",
    "generate_class_outline",
    "generate_instructor_guide",
    "generate_quick_reference",
    "generate_video_script",
    "instructor_guide_to_markdown",
    "outline_to_markdown",
    "quick_ref_to_markdown",
    "video_script_to_markdown",
    "extract_text_from_files",
]
