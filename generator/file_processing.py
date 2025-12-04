"""File processing utilities for extracting text from uploaded documents."""

from __future__ import annotations

import io
import os
from typing import List

import pdfplumber
import streamlit as st
from docx import Document
from streamlit.runtime.uploaded_file_manager import UploadedFile


def _extract_pdf(file: UploadedFile) -> str:
    try:
        with pdfplumber.open(io.BytesIO(file.getbuffer())) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(filter(None, pages))
    except Exception as exc:  # pragma: no cover - depends on file content
        st.error(f"Failed to read PDF {file.name}: {exc}")
        return ""


def _extract_docx(file: UploadedFile) -> str:
    try:
        document = Document(io.BytesIO(file.getbuffer()))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:  # pragma: no cover - depends on file content
        st.error(f"Failed to read DOCX {file.name}: {exc}")
        return ""


def _extract_txt(file: UploadedFile) -> str:
    try:
        return file.getvalue().decode("utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover - defensive
        st.error(f"Failed to read text file {file.name}: {exc}")
        return ""


def extract_text_from_files(uploaded_files: List[UploadedFile]) -> str:
    """Extract text from uploaded PDF, DOCX, and TXT files."""

    if not uploaded_files:
        return ""

    extracted_sections = []
    for file in uploaded_files:
        if not file:
            continue

        ext = os.path.splitext(file.name or "")[1].lower()
        if ext == ".pdf":
            text = _extract_pdf(file)
        elif ext in {".docx", ".doc"}:
            text = _extract_docx(file)
        elif ext == ".txt":
            text = _extract_txt(file)
        else:
            st.error(f"Unsupported file type for {file.name}.")
            text = ""

        if text:
            extracted_sections.append(f"[Source: {file.name}]\n{text}")

    return "\n\n".join(extracted_sections)


__all__ = ["extract_text_from_files"]
