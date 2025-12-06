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


# -------------------------------------------------------------------
# Render helpers
# -------------------------------------------------------------------


def _render_outline(outline: ClassOutline) -> None:
    if not outline.sections:
        st.info("No sections in the outline.")
        return

    st.subheader(outline.title)
    for section in outline.sections:
        st.markdown(f"### {section.title}")
        if section.objectives:
            st.markdown("**Objectives:**")
            st.markdown("\n".join(f"- {item}" for item in section.objectives))
        if section.subtopics:
            st.markdown("**Subtopics:**")
            st.markdown("\n".join(f"- {topic}" for topic in section.subtopics))
        if section.duration_minutes is not None:
            st.markdown(f"**Duration:** {section.duration_minutes} minutes")


def _render_instructor_guide(guide: InstructorGuide) -> None:
    # Training plan and goals
    if guide.training_plan_and_goals:
        st.subheader("Training plan and goals")
        st.write(guide.training_plan_and_goals)

    # Target audience
    if guide.target_audience:
        st.subheader("Target audience")
        st.write(guide.target_audience)

    # Prerequisites
    if guide.prerequisites:
        st.subheader("Prerequisites")
        st.write(guide.prerequisites)

    # Office 365 status
    if guide.office365_status:
        st.subheader("Office 365 status")
        st.write(guide.office365_status)

    # Learning objectives
    if guide.learning_objectives:
        st.subheader("Learning objectives")
        st.markdown("By the end of the session, participants will be able to:")
        st.markdown("\n".join(f"1. {obj}" for obj in guide.learning_objectives))

    # Preparation and course setup
    if (
        guide.required_materials_and_equipment
        or guide.instructor_setup
        or guide.participant_setup
        or guide.handouts
    ):
        st.subheader("Preparation and course setup")

        if guide.required_materials_and_equipment:
            st.markdown("**Required materials and equipment**")
            st.markdown("\n".join(f"- {item}" for item in guide.required_materials_and_equipment))

        if guide.instructor_setup:
            st.markdown("**Setup – instructor**")
            st.markdown("\n".join(f"- {item}" for item in guide.instructor_setup))

        if guide.participant_setup:
            st.markdown("**Setup – participants**")
            st.markdown("\n".join(f"- {item}" for item in guide.participant_setup))

        if guide.handouts:
            st.markdown("**Handouts (optional)**")
            st.markdown("\n".join(f"- {item}" for item in guide.handouts))

    # Type of class
    if guide.class_type:
        st.subheader("Type of class")
        st.write(guide.class_type)

    # Class checklist
    if (
        guide.class_checklist_before
        or guide.class_checklist_start
        or guide.class_checklist_after
    ):
        st.subheader("Class checklist")

        if guide.class_checklist_before:
            st.markdown("**Before class:**")
            st.markdown("\n".join(f"- {item}" for item in guide.class_checklist_before))

        if guide.class_checklist_start:
            st.markdown("**Start of class:**")
            st.markdown("\n".join(f"- {item}" for item in guide.class_checklist_start))

        if guide.class_checklist_after:
            st.markdown("**After class:**")
            st.markdown("\n".join(f"- {item}" for item in guide.class_checklist_after))

    # Instructional framework topics
    if guide.sections:
        st.subheader("Instructional framework")
        for section in guide.sections:
            st.markdown(f"### Topic: {section.title}")
            if section.estimated_time_minutes:
                st.markdown(f"**Estimated Time:** {section.estimated_time_minutes} minutes")

            if section.learning_objectives:
                st.markdown("**Learning Objectives**")
                st.markdown("\n".join(f"- {obj}" for obj in section.learning_objectives))

            if section.instructional_steps:
                st.markdown("**Instructional Steps:**")
                st.markdown("\n".join(f"- {step}" for step in section.instructional_steps))

            if section.key_points:
                st.markdown("**Key Points:**")
                st.markdown("\n".join(f"- {kp}" for kp in section.key_points))


def _render_video_script(script: VideoScript) -> None:
    if not script.segments:
        st.info("No segments in the video script.")
        return

    for idx, segment in enumerate(script.segments, start=1):
        st.markdown(f"### Segment {idx}: {segment.title}")
        if segment.narration:
            st.markdown("**Narration:**")
            st.markdown(segment.narration)
        if segment.screen_directions:
            st.markdown("**Screen Directions:**")
            st.markdown(segment.screen_directions)
        if segment.approx_duration_seconds is not None:
            st.markdown(f"**Approx Duration:** {segment.approx_duration_seconds} seconds")


def _render_qrg(qrg: QuickReferenceGuide) -> None:
    if not qrg.steps:
        st.info("No steps in the quick reference guide.")
        return

    for step in qrg.steps:
        st.markdown(f"### Step {step.step_number}: {step.title}")
        st.markdown(f"**Action:** {step.action}")
        if step.notes:
            st.markdown(f"**Notes:** {step.notes}")


# -------------------------------------------------------------------
# App layout & state
# -------------------------------------------------------------------

st.set_page_config(page_title="Training Class Generator", layout="wide")

st.title("Training Class Generator")
st.write(
    "Upload training documents and/or audio, and generate a class outline, "
    "instructor guide, video script, and quick reference guide."
)

# Initialize session state containers
st.session_state.setdefault("generated_package", None)
st.session_state.setdefault("combined_text", "")
st.session_state.setdefault("tts_payload", None)

# Inputs (single set of widgets with explicit keys)
course_title = st.text_input("Course Title", value="", key="course_title_input")

class_type = st.selectbox(
    "Class Type",
    ["Full Class", "Short Video", "Quick Reference Only"],
    key="class_type_select",
)

document_uploads = st.file_uploader(
    "Upload training/source documents (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="document_uploads",
)

audio_uploads = st.file_uploader(
    "Upload audio files for transcription (optional)",
    type=["wav", "mp3", "m4a"],
    accept_multiple_files=True,
    key="audio_uploads",
)

generate_clicked = st.button(
    "Generate Training Package",
    type="primary",
    key="generate_package_button",
)

# -------------------------------------------------------------------
# Generation flow
# -------------------------------------------------------------------

if generate_clicked:
    if not course_title:
        st.error("Please enter a course title.")
    elif not document_uploads and not audio_uploads:
        st.error("Please upload at least one document or audio file.")
    else:
        with st.spinner("Generating training package..."):
            # Extract text from documents
            document_text = extract_text_from_files(document_uploads)

            # Transcribe audio
            transcript_text = transcribe_audio_files(audio_uploads)

            # Combine text and transcript
            combined_text_parts = []
            if document_text:
                combined_text_parts.append(document_text)
            if transcript_text:
                combined_text_parts.append("[Audio Transcript]\n" + transcript_text)
            full_text = "\n\n".join(combined_text_parts).strip()

            # If everything failed, fall back to a simple message so the LLM has *something*
            if not full_text:
                full_text = (
                    "No usable source text was extracted. "
                    "Create a generic but reasonable training package based only on the course title and class type."
                )

            # Call generators
            outline = generate_class_outline(full_text, course_title, class_type)
            instructor_guide = generate_instructor_guide(full_text, course_title, class_type)
            video_script = generate_video_script(full_text, course_title, class_type)
            quick_reference = generate_quick_reference(full_text, course_title, class_type)

            # Store in session_state
            st.session_state.generated_package = {
                "outline": outline,
                "instructor_guide": instructor_guide,
                "video_script": video_script,
                "quick_reference": quick_reference,
            }
            st.session_state.combined_text = full_text
            st.session_state.tts_payload = None

        st.success("Training package generated!")


# -------------------------------------------------------------------
# Display results
# -------------------------------------------------------------------

package = st.session_state.get("generated_package")

if package:
    tabs = st.tabs(["Outline", "Instructor Guide", "Video Script", "Quick Reference"])

    # Outline tab
    with tabs[0]:
        st.header("Class Outline")
        _render_outline(package["outline"])
        outline_md = outline_to_markdown(package["outline"])
        st.download_button(
            "Download Outline (.md)",
            outline_md,
            file_name="class_outline.md",
            key="download_outline",
        )

    # Instructor Guide tab
    with tabs[1]:
        st.header("Instructor Guide")
        _render_instructor_guide(package["instructor_guide"])
        instructor_md = instructor_guide_to_markdown(package["instructor_guide"])
        st.download_button(
            "Download Instructor Guide (.md)",
            instructor_md,
            file_name="instructor_guide.md",
            key="download_instructor_guide",
        )

    # Video Script tab
    with tabs[2]:
        st.header("Video Script")
        _render_video_script(package["video_script"])
        video_md = video_script_to_markdown(package["video_script"])
        st.download_button(
            "Download Video Script (.md)",
            video_md,
            file_name="video_script.md",
            key="download_video_script",
        )

        # Generate TTS audio
        if st.button("Generate Narration Audio (TTS)", key="generate_tts_button"):
            with st.spinner("Generating narration audio..."):
                st.session_state.tts_payload = synthesize_narration_audio(
                    package["video_script"]
                )

        # If TTS exists, show preview players + download buttons
        if st.session_state.tts_payload:
            st.info("Preview and download narration segments below.")
            for filename, payload in st.session_state.tts_payload.items():
                st.markdown(f"**{filename}**")
                # Inline audio player preview
                st.audio(payload, format="audio/wav")
                # Download button
                st.download_button(
                    f"Download {filename}",
                    payload,
                    file_name=filename,
                    key=f"download_tts_{filename}",
                )

    # Quick Reference tab
    with tabs[3]:
        st.header("Quick Reference Guide")
        _render_qrg(package["quick_reference"])
        qrg_md = quick_ref_to_markdown(package["quick_reference"])
        st.download_button(
            "Download QRG (.md)",
            qrg_md,
            file_name="quick_reference.md",
            key="download_qrg",
        )

    # Combined source text (for debugging / transparency)
    with st.expander("Show combined source text used for generation"):
        st.write(st.session_state.combined_text or "No source text available.")
else:
    st.info("Upload documents and/or audio, enter a title, and click **Generate Training Package** to begin.")
