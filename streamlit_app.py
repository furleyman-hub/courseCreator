"""Streamlit UI for the Training Package Generator backend."""
from __future__ import annotations

import os
from io import BytesIO
from typing import Dict, List

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Training Package Generator", layout="wide")
st.title("Training Package Generator")
st.write("Upload source material and generate outlines, guides, scripts, and quick references in your browser.")


def outline_to_md(outline: Dict) -> str:
    lines: List[str] = [f"# {outline.get('title', 'Class Outline')}"]
    for section in outline.get("sections", []):
        lines.append(f"## {section.get('title', 'Section')}")
        objectives = section.get("objectives", []) or []
        if objectives:
            lines.append("**Objectives**")
            lines.extend([f"- {obj}" for obj in objectives])
        duration = section.get("durationMinutes")
        if duration:
            lines.append(f"_Duration: {duration} minutes_")
    return "\n\n".join(lines)


def instructor_to_md(guide: Dict) -> str:
    lines: List[str] = [f"# Instructor Guide: {guide.get('courseTitle', '')}"]
    for section in guide.get("sections", []):
        lines.append(f"## {section.get('title', 'Section')}")
        for label, key in (
            ("Learning Objectives", "learningObjectives"),
            ("Talking Points", "talkingPoints"),
            ("Suggested Activities", "suggestedActivities"),
        ):
            entries = section.get(key, []) or []
            if entries:
                lines.append(f"**{label}**")
                lines.extend([f"- {entry}" for entry in entries])
        timing = section.get("timingMinutes")
        if timing:
            lines.append(f"_Timing: {timing} minutes_")
    return "\n\n".join(lines)


def video_to_md(video: Dict) -> str:
    lines: List[str] = [f"# Video Script: {video.get('courseTitle', '')}"]
    for segment in video.get("segments", []):
        lines.append(f"## {segment.get('title', 'Segment')}")
        narration = segment.get("narration")
        if narration:
            lines.append("**Narration**")
            lines.append(narration)
        directions = segment.get("screenDirections")
        if directions:
            lines.append("**Screen Directions**")
            lines.append(directions)
        duration = segment.get("durationSeconds")
        if duration:
            lines.append(f"_Duration: {duration} seconds_")
    return "\n\n".join(lines)


def qrg_to_md(qrg: Dict) -> str:
    lines: List[str] = [f"# Quick Reference Guide: {qrg.get('courseTitle', '')}"]
    for step in qrg.get("steps", []):
        num = step.get("stepNumber")
        title = step.get("title", "Step")
        lines.append(f"## Step {num}: {title}")
        action = step.get("action")
        if action:
            lines.append(f"- **Action:** {action}")
        notes = step.get("notes")
        if notes:
            lines.append(f"- **Notes:** {notes}")
    return "\n\n".join(lines)


def download_button(label: str, content: str, filename: str):
    st.download_button(label, content, file_name=filename, mime="text/markdown")


def render_artifacts(artifacts: Dict):
    outline, instructor, video, qrg = (
        artifacts.get("classOutline"),
        artifacts.get("instructorGuide"),
        artifacts.get("videoScript"),
        artifacts.get("quickReferenceGuide"),
    )
    tabs = st.tabs(["Outline", "Instructor Guide", "Video Script", "Quick Reference"])

    with tabs[0]:
        st.markdown(outline_to_md(outline))
        download_button("Download Outline (.md)", outline_to_md(outline), "class_outline.md")

    with tabs[1]:
        st.markdown(instructor_to_md(instructor))
        download_button("Download Instructor Guide (.md)", instructor_to_md(instructor), "instructor_guide.md")

    with tabs[2]:
        st.markdown(video_to_md(video))
        download_button("Download Video Script (.md)", video_to_md(video), "video_script.md")

    with tabs[3]:
        st.markdown(qrg_to_md(qrg))
        download_button("Download QRG (.md)", qrg_to_md(qrg), "quick_reference.md")


st.sidebar.header("Settings")
st.sidebar.write("Set the backend API base URL (FastAPI app).")
backend_url = st.sidebar.text_input("Backend URL", BACKEND_URL)
st.sidebar.caption("Defaults to http://localhost:8000")

st.markdown("---")

with st.form(key="upload_form"):
    course_title = st.text_input("Course Title", value="")
    class_type = st.selectbox("Class Type", ["Full Class", "Short Video", "Quick Reference Only"])
    uploaded_files = st.file_uploader(
        "Upload training/source documents", type=["pdf", "doc", "docx", "txt"], accept_multiple_files=True
    )
    submitted = st.form_submit_button("Generate Training Package")

if submitted:
    if not course_title:
        st.error("Please enter a course title.")
    elif not uploaded_files:
        st.error("Please upload at least one file.")
    else:
        with st.spinner("Uploading and extracting text..."):
            files_payload = []
            for file in uploaded_files:
                bytes_data = file.getvalue()
                files_payload.append(("files", (file.name, BytesIO(bytes_data), file.type or "application/octet-stream")))
            try:
                upload_resp = requests.post(
                    f"{backend_url}/api/upload",
                    data={"courseTitle": course_title, "classType": class_type},
                    files=files_payload,
                    timeout=120,
                )
                upload_resp.raise_for_status()
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")
                st.stop()

            upload_data = upload_resp.json()
            st.session_state["last_upload"] = upload_data
            st.success("Files uploaded and text extracted.")

        with st.spinner("Generating training package..."):
            try:
                generate_resp = requests.post(
                    f"{backend_url}/api/generate",
                    json={
                        "extractedText": upload_data.get("extractedText", ""),
                        "courseTitle": course_title,
                        "classType": class_type,
                    },
                    timeout=120,
                )
                generate_resp.raise_for_status()
            except requests.RequestException as exc:
                st.error(f"Generation failed: {exc}")
                st.stop()

            artifacts = generate_resp.json()
            st.session_state["artifacts"] = artifacts
            st.success("Training package generated!")

if upload_data := st.session_state.get("last_upload"):
    with st.expander("Extracted text preview"):
        st.write(upload_data.get("extractedText", ""))

if "artifacts" in st.session_state:
    render_artifacts(st.session_state["artifacts"])
