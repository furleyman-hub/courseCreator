"""Unified text extraction from uploaded PDF, DOCX, and TXT files."""

from __future__ import annotations

import io
from typing import List

import pdfplumber
import docx
from streamlit.runtime.uploaded_file_manager import UploadedFile


def _extract_pdf(file: UploadedFile) -> str:
    """Extract text from a PDF using pdfplumber."""
    try:
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
    except Exception as exc:
        return f"[PDF extraction failed for {file.name}: {exc}]"


def _extract_docx(file: UploadedFile) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = docx.Document(io.BytesIO(file.read()))
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
        filename = file.name.lower()

        if filename.endswith(".pdf"):
            sections.append(_extract_pdf(file))

        elif filename.endswith(".docx"):
            sections.append(_extract_docx(file))

        elif filename.endswith(".txt"):
            sections.append(_extract_txt(file))

        else:
            sections.append(f"[Unsupported file type: {file.name}]")

    return "\n\n".join(sections)
