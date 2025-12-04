"""Streamlit app for generating training packages from documents and audio."""

from __future__ import annotations

import streamlit as st

import generator.llm_openai as llm
from generator import (
    ClassOutline,
    InstructorGuide,
    QuickReferenceGuide,
    VideoScript,
    extract_text_from_files,
    instructor_guide_to_markdown,
    outline_to_markdown,
    quick_ref_to_markdown,
    video_script_to_markdown,
)
from generator.audio_processing import synthesize_narration_audio, transcribe_audio_files


def _render_outline(outline: ClassOutline):
    for section in outline.sections:
        st.subheader(section.title)
        if section.objectives:
            st.markdown("**Objectives:**")
            st.markdown("\n".join(f"- {item}" for item in section.objectives))
        if section.subtopics:
            st.markdown("**Subtopics:**")
            st.markdown("\n".join(f"  - {topic}" for topic in section.subtopics))
        if section.duration_minutes is not None:
            st.markdown(f"**Duration:** {section.duration_minutes} minutes")


def _render_instructor_guide(guide: InstructorGuide):
    for section in guide.sections:
        st.subheader(section.title)
        if section.learning_objectives:
            st.markdown("**Learning Objectives:**")
            st.markdown("\n".join(f"- {item}" for item in section.learning_objectives))
        if section.talking_points:
            st.markdown("**Talking Points:**")
            st.markdown("\n".join(f"- {item}" for item in section.talking_points))
        if section.suggested_activities:
            st.markdown("**Suggested Activities:**")
            st.markdown("\n".join(f"- {item}" for item in section.suggested_activities))
        if section.estimated_time_minutes is not None:
            st.markdown(f"**Estimated Time:** {section.estimated_time_minutes} minutes")


def _render_video_script(script: VideoScript):
    for idx, segment in enumerate(script.segments, start=1):
        st.subheader(f"Segment {idx}: {segment.title}")
        st.markdown("**Narration:**")
        st.markdown(segment.narration)
        st.markdown("**Screen Directions:**")
        st.markdown(segment.screen_directions)
        if segment.approx_duration_seconds is not None:
            st.markdown(f"**Approx Duration:** {segment.approx_duration_seconds} seconds")


def _render_qrg(qrg: QuickReferenceGuide):
    for step in qrg.steps:
        st.subheader(f"Step {step.step_number}: {step.title}")
        st.markdown(f"**Action:** {step.action}")
        if step.notes:
            st.markdown(f"**Notes:** {step.notes}")


st.set_page_config(page_title="Training Class Generator", layout="wide")
st.title("Training Class Generator")
st.write(
    "Upload documents and/or audio to generate outlines, guides, scripts, and quick references. "
    "You can use either source type or combine both."
)

course_title = st.text_input(
    "Course Title",
    value="",
    key="course_title_main",
)
class_type = st.selectbox(
    "Class Type", ["Full Class", "Short Video", "Quick Reference Only"], key="class_type_main"
)
document_uploads = st.file_uploader(
    "Upload training/source documents",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="document_uploader_main",
)
audio_uploads = st.file_uploader(
    "Upload audio files for transcription",
    type=["wav", "mp3", "m4a"],
    accept_multiple_files=True,
    key="audio_uploader_main",
)

if "generated_package" not in st.session_state:
    st.session_state.generated_package = None
if "combined_text" not in st.session_state:
    st.session_state.combined_text = ""
if "tts_payload" not in st.session_state:
    st.session_state.tts_payload = None


if st.button("Generate Training Package", type="primary", key="generate_package_btn"):
    if not course_title:
        st.error("Please enter a course title.")
    elif not document_uploads and not audio_uploads:
        st.error("Please upload at least one document or at least one audio file.")
    else:
        with st.spinner("Generating training package..."):
            try:
                document_text = extract_text_from_files(document_uploads)
            except Exception as exc:  # pragma: no cover - defensive
                st.error(f"Document processing failed: {exc}")
                document_text = ""

            try:
                transcript_text = transcribe_audio_files(audio_uploads)
            except Exception as exc:  # pragma: no cover - defensive
                st.error(f"Audio transcription failed: {exc}")
                transcript_text = ""

            combined_text_parts = []
            if document_text:
                combined_text_parts.append(document_text)
            if transcript_text:
                combined_text_parts.append("[Audio Transcript]\n" + transcript_text)
            full_text = "\n\n".join(combined_text_parts)

            try:
                outline = llm.generate_class_outline(full_text, course_title, class_type)
                instructor_guide = llm.generate_instructor_guide(full_text, course_title, class_type)
                video_script = llm.generate_video_script(full_text, course_title, class_type)
                quick_reference = llm.generate_quick_reference(full_text, course_title, class_type)
            except Exception as exc:  # pragma: no cover - defensive
                st.error(f"Failed to generate training content: {exc}")
            else:
                st.session_state.generated_package = {
                    "outline": outline,
                    "instructor_guide": instructor_guide,
                    "video_script": video_script,
                    "quick_reference": quick_reference,
                }
                st.session_state.combined_text = full_text
                st.session_state.tts_payload = None
                st.success("Training package generated!")


package = st.session_state.generated_package
if package:
    tabs = st.tabs(
        ["Outline", "Instructor Guide", "Video Script", "Quick Reference"], key="results_tabs"
    )

    with tabs[0]:
        st.header("Class Outline")
        _render_outline(package["outline"])
        outline_md = outline_to_markdown(package["outline"])
        st.download_button(
            "Download Outline (.md)",
            outline_md,
            file_name="class_outline.md",
            key="download_outline_md",
        )

    with tabs[1]:
        st.header("Instructor Guide")
        _render_instructor_guide(package["instructor_guide"])
        instructor_md = instructor_guide_to_markdown(package["instructor_guide"])
        st.download_button(
            "Download Instructor Guide (.md)",
            instructor_md,
            file_name="instructor_guide.md",
            key="download_instructor_md",
        )

    with tabs[2]:
        st.header("Video Script")
        _render_video_script(package["video_script"])
        video_md = video_script_to_markdown(package["video_script"])
        st.download_button(
            "Download Video Script (.md)",
            video_md,
            file_name="video_script.md",
            key="download_video_script_md",
        )

        if st.button("Generate Narration Audio (TTS)", key="generate_tts_btn"):
            with st.spinner("Generating narration audio..."):
                st.session_state.tts_payload = synthesize_narration_audio(package["video_script"])

        if st.session_state.tts_payload:
            st.info("Download generated narration segments below.")
            for idx, (filename, payload) in enumerate(st.session_state.tts_payload.items(), start=1):
                st.download_button(
                    label=f"Download {filename}",
                    data=payload,
                    file_name=filename,
                    mime="audio/mpeg",
                    key=f"download_tts_{idx}_{filename}",
                )

    with tabs[3]:
        st.header("Quick Reference Guide")
        _render_qrg(package["quick_reference"])
        qrg_md = quick_ref_to_markdown(package["quick_reference"])
        st.download_button(
            "Download QRG (.md)",
            qrg_md,
            file_name="quick_reference.md",
            key="download_qrg_md",
        )

    with st.expander("Show combined source text", expanded=False, key="combined_text_expander"):
        st.write(st.session_state.combined_text or "No text available.")
