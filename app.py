"""All-in-one Streamlit app for generating training packages."""
from __future__ import annotations

from typing import List, Tuple

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from backend.models.types import GenerateResponse
from backend.services.formatting import artifacts_to_md
from backend.services.pipeline import generate_training_package


st.set_page_config(page_title="Training Package Generator", layout="wide")
st.title("Training Package Generator")
st.write(
    "Upload source material and generate outlines, guides, scripts, and quick references directly in Streamlit."
)


def _validate_inputs(course_title: str, files: List[UploadedFile]) -> Tuple[bool, str]:
    if not course_title:
        return False, "Please enter a course title."
    if not files:
        return False, "Please upload at least one file."
    return True, ""


with st.sidebar:
    st.header("Session Settings")
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Optional. If omitted, fallback templates are used unless OPENAI_API_KEY is set in the environment.",
    )
    st.caption("No HTTP calls are made; all processing runs in this app.")


with st.form(key="upload_form"):
    course_title = st.text_input("Course Title", value="")
    class_type = st.selectbox("Class Type", ["Full Class", "Short Video", "Quick Reference Only"])
    uploaded_files = st.file_uploader(
        "Upload training/source documents",
        type=["pdf", "doc", "docx", "txt"],
        accept_multiple_files=True,
    )
    submitted = st.form_submit_button("Generate Training Package")


if submitted:
    ok, error_msg = _validate_inputs(course_title, uploaded_files)
    if not ok:
        st.error(error_msg)
    else:
        with st.spinner("Extracting text and generating artifacts..."):
            contents = [file.getvalue() for file in uploaded_files]
            filenames = [file.name or "upload" for file in uploaded_files]
            extracted_text, artifacts = generate_training_package(
                contents, filenames, course_title, class_type, api_key=openai_api_key or None
            )
            st.session_state["extracted_text"] = extracted_text
            st.session_state["artifacts"] = artifacts
        st.success("Training package generated!")


if "extracted_text" in st.session_state:
    with st.expander("Extracted text preview"):
        st.write(st.session_state["extracted_text"])


if "artifacts" in st.session_state:
    artifacts: GenerateResponse = st.session_state["artifacts"]
    md_payload = artifacts_to_md(artifacts.dict())
    tabs = st.tabs(["Outline", "Instructor Guide", "Video Script", "Quick Reference"])

    with tabs[0]:
        st.markdown(md_payload["outline"])
        st.download_button("Download Outline (.md)", md_payload["outline"], file_name="class_outline.md")

    with tabs[1]:
        st.markdown(md_payload["instructor"])
        st.download_button("Download Instructor Guide (.md)", md_payload["instructor"], file_name="instructor_guide.md")

    with tabs[2]:
        st.markdown(md_payload["video"])
        st.download_button("Download Video Script (.md)", md_payload["video"], file_name="video_script.md")

    with tabs[3]:
        st.markdown(md_payload["qrg"])
        st.download_button("Download QRG (.md)", md_payload["qrg"], file_name="quick_reference.md")
