"""Stubbed text extraction from uploaded files."""

from __future__ import annotations

from typing import List

from streamlit.runtime.uploaded_file_manager import UploadedFile


# In the future, you can leverage libraries such as:
# - pypdf for PDF parsing
# - python-docx for Word documents

def extract_text_from_files(uploaded_files: List[UploadedFile]) -> str:
    """Combine text extracted from uploaded files.

    This placeholder implementation concatenates file names and example text.
    Replace the stubbed extraction with real parsing logic when ready.
    """

    if not uploaded_files:
        return ""

    extracted_sections = []
    for file in uploaded_files:
        file_label = file.name or "uploaded_file"
        # TODO: replace with actual text extraction logic
        extracted_sections.append(f"[Extracted content from {file_label}]\nSample text for {file_label}.")

    return "\n\n".join(extracted_sections)
