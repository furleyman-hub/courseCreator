"""Streamlit app for generating training packages from documents and audio."""

from __future__ import annotations

import streamlit as st

from generator import (
    ClassOutline,
    InstructorGuide,
    QuickReferenceGuide,
    VideoScript,
    extract_text_from_files,
    generate_class_outline,
    generate_instructor_guide,
    generate_quick_reference,
    generate_video_script,
    instructor_guide_to_markdown,
    outline_to_markdown,
    quick_ref_to_markdown,
    synthesize_narration_audio,
    transcribe_audio_files,
    video_script_to_markdown,
)


def _render_outline(outline: ClassOutline) -> None:
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


def _render_instructor_guide(guide: InstructorGuide) -> None:
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


def _render_video_script(script: VideoScript) -> None:
    for idx, segment in enumerate(script.segments, start=1):
        st.subheader(f"Segment {idx}: {segment.title}")
        st.markdown("**Narration:**")
        st.markdown(segment.narration)
        st.markdown("**Screen Directions:**")
        st.markdown(segment.screen_directions)
        if segment.approx_duration_seconds is not None:
            st.markdown(f"**Approx Duration:** {segment.approx_duration_seconds} seconds")


def _render_qrg(qrg: QuickReferenceGuide) -> None:
    for step in qrg.steps:
        st.subheader(f"Step {step.step_number}: {step.title}")
        st.markdown(f"**Action:** {step.action}")
        if step.notes:
            st.markdown(f"**Notes:** {step.notes}")


# ------------------------------------------------------------
# Page config and intro
# ------------------------------------------------------------
st.set_page_config(page_title="Training Class Generator", layout="wide")
st.title("Training Class Generator")
st.write(
    "Upload documents and audio to generate class outlines, instructor guides, "
    "video scripts, and quick reference guides."
)

# ------------------------------------------------------------
# Initialize session state
# ------------------------------------------------------------
if "generated_package" not in st.session_state:
    st.session_state.generated_package = None
if "combined_text" not in st.session_state:
    st.session_state.combined_text = ""
if "tts_payload" not in st.session_state:
    st.session_state.tts_payload = None

# ------------------------------------------------------------
# Input widgets (each defined ONCE, with unique keys)
# ------------------------------------------------------------
course_title = st.text_input(
    "Course Title",
    value="",
    key="course_title_main",
)

class_type = st.selectbox(
    "Class Type",
    ["Full Class", "Short Video", "Quick Reference Only"],
    key="class_type_select",
)

document_uploads = st.file_uploader(
    "Upload training/source documents",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="document_uploader",
)

audio_uploads = st.file_uploader(
    "Upload audio files for transcription",
    type=["wav", "mp3", "m4a"],
    accept_multiple_files=True,
    key="audio_uploader",
)

generate_clicked = st.button(
    "Generate Training Package",
    type="primary",
    key="generate_package_button",
)

# ------------------------------------------------------------
# Generation logic
# ------------------------------------------------------------
if generate_clicked:
    if not course_title:
        st.error("Please enter a course title.")
    elif not document_uploads and not audio_uploads:
        st.error("Please upload at least one document or audio file.")
    else:
        with st.spinner("Generating training package..."):
            document_text = extract_text_from_files(document_uploads)
            transcript_text = transcribe_audio_files(audio_uploads)

            combined_text_parts: list[str] = []
            if document_text:
                combined_text_parts.append(document_text)
            if transcript_text:
                combined_text_parts.append("[Audio Transcript]\n" + transcript_text)
            full_text = "\n\n".join(combined_text_parts)

            outline = generate_class_outline(full_text, course_title, class_type)
            instructor_guide = generate_instructor_guide(full_text, course_title, class_type)
            video_script = generate_video_script(full_text, course_title, class_type)
            quick_reference = generate_quick_reference(full_text, course_title, class_type)

            st.session_state.generated_package = {
                "outline": outline,
                "instructor_guide": instructor_guide,
                "video_script": video_script,
                "quick_reference": quick_reference,
            }
            st.session_state.combined_text = full_text
            st.session_state.tts_payload = None

        st.success("Training package generated!")

# ------------------------------------------------------------
# Results display
# ------------------------------------------------------------
package = st.session_state.generated_package
if package:
    tabs = st.tabs(["Outline", "Instructor Guide", "Video Script", "Quick Reference"])

    with tabs[0]:
        st.header("Class Outline")
        _render_outline(package["outline"])
        outline_md = outline_to_markdown(package["outline"])
        st.download_button(
            "Download Outline (.md)",
            outline_md,
            file_name="class_outline.md",
        )

    with tabs[1]:
        st.header("Instructor Guide")
        _render_instructor_guide(package["instructor_guide"])
        instructor_md = instructor_guide_to_markdown(package["instructor_guide"])
        st.download_button(
            "Download Instructor Guide (.md)",
            instructor_md,
            file_name="instructor_guide.md",
        )

    with tabs[2]:
        st.header("Video Script")
        _render_video_script(package["video_script"])
        video_md = video_script_to_markdown(package["video_script"])
        st.download_button(
            "Download Video Script (.md)",
            video_md,
            file_name="video_script.md",
        )

        tts_clicked = st.button(
            "Generate Narration Audio (TTS)",
            key="generate_tts_button",
        )

        if tts_clicked:
            with st.spinner("Generating narration audio..."):
                st.session_state.tts_payload = synthesize_narration_audio(package["video_script"])

        if st.session_state.tts_payload:
            st.info("Download generated narration segments below.")
            for filename, payload in st.session_state.tts_payload.items():
                st.download_button(
                    label=f"Download {filename}",
                    data=payload,
                    file_name=filename,
                    key=f"tts_download_{filename}",
                )

    with tabs[3]:
        st.header("Quick Reference Guide")
        _render_qrg(package["quick_reference"])
        qrg_md = quick_ref_to_markdown(package["quick_reference"])
        st.download_button(
            "Download QRG (.md)",
            qrg_md,
            file_name="quick_reference.md",
        )

    with st.expander("Show combined source text"):
        st.write(st.session_state.combined_text or "No text available.")
