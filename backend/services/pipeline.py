from pathlib import Path
from typing import Iterable, Optional, Tuple
import tempfile

from backend.models.types import GenerateResponse
from backend.services.extraction import extract_text_from_files, save_uploaded_files
from backend.services import llm


def extract_text_from_uploads(files: Iterable[bytes], filenames: Iterable[str]) -> str:
    """Persist uploaded bytes temporarily and return combined text."""

    with tempfile.TemporaryDirectory() as tmpdir:
        upload_dir = Path(tmpdir)
        saved = save_uploaded_files(list(files), list(filenames), upload_dir)
        return extract_text_from_files(saved)


def build_artifacts(
    extracted_text: str,
    course_title: str,
    class_type: str,
    api_key: Optional[str] = None,
) -> GenerateResponse:
    """Generate all artifacts from extracted text and metadata."""

    outline = llm.generate_class_outline(extracted_text, course_title, class_type, api_key)
    instructor = llm.generate_instructor_guide(extracted_text, course_title, class_type, api_key)
    video = llm.generate_video_script(extracted_text, course_title, class_type, api_key)
    qrg = llm.generate_quick_reference(extracted_text, course_title, class_type, api_key)

    return GenerateResponse(
        classOutline=outline,
        instructorGuide=instructor,
        videoScript=video,
        quickReferenceGuide=qrg,
    )


def generate_training_package(
    files: Iterable[bytes],
    filenames: Iterable[str],
    course_title: str,
    class_type: str,
    api_key: Optional[str] = None,
) -> Tuple[str, GenerateResponse]:
    """Convenience helper that extracts text and builds artifacts in one go."""

    extracted_text = extract_text_from_uploads(files, filenames)
    artifacts = build_artifacts(extracted_text, course_title, class_type, api_key)
    return extracted_text, artifacts
