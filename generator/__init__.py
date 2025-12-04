from .generator import (
    generate_class_outline,
    generate_instructor_guide,
    generate_quick_reference,
    generate_video_script,
)

from .models import (
    ClassOutline,
    OutlineSection,
    InstructorGuide,
    InstructorSection,
    VideoScript,
    VideoSegment,
    QuickReferenceGuide,
    QuickRefStep,
)

from .markdown_utils import (
    outline_to_markdown,
    instructor_guide_to_markdown,
    video_script_to_markdown,
    quick_ref_to_markdown,
)

from .extract_text import extract_text_from_files
from .audio import transcribe_audio_files, synthesize_narration_audio


__all__ = [
    "generate_class_outline",
    "generate_instructor_guide",
    "generate_quick_reference",
    "generate_video_script",
    "outline_to_markdown",
    "instructor_guide_to_markdown",
    "video_script_to_markdown",
    "quick_ref_to_markdown",
    "extract_text_from_files",
    "transcribe_audio_files",
    "synthesize_narration_audio",
    # models
    "ClassOutline",
    "OutlineSection",
    "InstructorGuide",
    "InstructorSection",
    "VideoScript",
    "VideoSegment",
    "QuickReferenceGuide",
    "QuickRefStep",
]
