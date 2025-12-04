"""Unified text extraction from uploaded PDF, DOCX, and TXT files."""

from __future__ import annotations

import io
from typing import List

from pypdf import PdfReader
import docx
from streamlit.runtime.uploaded_file_manager import UploadedFile


def _extract_pdf(file: UploadedFile) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        # Read the uploaded file into memory
        data = file.read()
        pdf_stream = io.BytesIO(data)
        reader = PdfReader(pdf_stream)

        pages_text = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")

        return "\n".join(pages_text)
    except Exception as exc:
        return f"[PDF extraction failed for {file.name}: {exc}]"


def _extract_docx(file: UploadedFile) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        data = file.read()
        doc_stream = io.BytesIO(data)
        doc = docx.Document(doc_stream)
        paras = [p.text for p in doc.paragraphs]
        return "\n".join(paras)
    except Exception as exc:
        return f"[DOCX extraction failed for {file.name}: {exc}]"


def _extract_txt(file: UploadedFile) -> str:
    """Extract text from a plain text file."""
    try:
        return file.read().decode("utf-8", errors="ignore")
    except Exception as exc:
        return f"[TXT extraction failed for {file.name}: {exc}]"


def extract_text_from_files(uploaded_files: List[UploadedFile]) -> str:
    """Extract and combine text from uploaded documents.

    Supports PDF, DOCX, and TXT files.
    Returns a single combined text string.
    """

    if not uploaded_files:
        return ""

    sections = []

    for file in uploaded_files:
        filename = (file.name or "").lower()

        if filename.endswith(".pdf"):
            sections.append(_extract_pdf(file))
        elif filename.endswith(".docx"):
            sections.append(_extract_docx(file))
        elif filename.endswith(".txt"):
            sections.append(_extract_txt(file))
        else:
            sections.append(f"[Unsupported file type: {file.name}]")

    return "\n\n".join(sections)
