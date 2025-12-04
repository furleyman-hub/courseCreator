"""Unified text extraction from uploaded PDF, DOCX, and TXT files."""

from __future__ import annotations

import io
from typing import List

from pypdf import PdfReader
import docx
from streamlit.runtime.uploaded_file_manager import UploadedFile


# -----------------------------------------------------------
# PDF extraction
# -----------------------------------------------------------

def _extract_pdf(file: UploadedFile) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        data = file.read()
        pdf_stream = io.BytesIO(data)
        reader = PdfReader(pdf_stream)

        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        output = "\n".join(pages).strip()
        if not output:
            return f"[PDF contained no extractable text: {file.name}]"

        return output

    except Exception as exc:
        return f"[PDF extraction failed for {file.name}: {exc}]"


# -----------------------------------------------------------
# DOCX extraction
# -----------------------------------------------------------

def _extract_docx(file: UploadedFile) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        data = file.read()
        stream = io.BytesIO(data)
        document = docx.Document(stream)

        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        output = "\n".join(paragraphs).strip()

        if not output:
            return f"[DOCX contained no extractable text: {file.name}]"

        return output

    except Exception as exc:
        return f"[DOCX extraction failed for {file.name}: {exc}]"


# -----------------------------------------------------------
# TXT extraction
# -----------------------------------------------------------

def _extract_txt(file: UploadedFile) -> str:
    """Extract UTF-8 text from .txt files."""
    try:
        data = file.read()
        return data.decode("utf-8", errors="ignore").strip()
    except Exception as exc:
        return f"[TXT extraction failed for {file.name}: {exc}]"


# -----------------------------------------------------------
# Public API
# -----------------------------------------------------------

def extract_text_from_files(uploaded_files: List[UploadedFile]) -> str:
    """
    Extract and combine text from uploaded documents.

    Supports:
    - PDF
    - DOCX
    - TXT

    Returns:
        A single combined string used by the training generator.
    """
    if not uploaded_files:
        return ""

    extracted_sections = []

    for file in uploaded_files:
        name = (file.name or "").lower()

        if name.endswith(".pdf"):
            extracted_sections.append(_extract_pdf(file))
        elif name.endswith(".docx"):
            extracted_sections.append(_extract_docx(file))
        elif name.endswith(".txt"):
            extracted_sections.append(_extract_txt(file))
        else:
            extracted_sections.append(f"[Unsupported file type: {file.name}]")

    return "\n\n".join(extracted_sections).strip()
