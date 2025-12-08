"""Streamlit app for generating training packages from documents and audio."""

from __future__ import annotations

import streamlit as st

from notes_ocr import extract_text_from_note_images

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

import heygen_client

# -------------------------------------------------------------------
# Page config + CSS
# -------------------------------------------------------------------

st.set_page_config(page_title="Training Class Generator", layout="wide")

# Narrow, compact layout
st.markdown(
    """
<style>
    /* Make main content narrower and centered */
    .block-container {
        max-width: 900px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Tighten vertical spacing between widgets */
    div.stMarkdown, div.stTextInput, div.stSelectbox, div.stFileUploader,
    div[data-testid="stHorizontalBlock"] {
        margin-bottom: 0.3rem !important;
    }

    /* Section headers smaller and tighter */
    h2, h3 {
        margin-top: 0.6rem !important;
        margin-bottom: 0.3rem !important;
    }

    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    /* Dividers closer together */
    hr {
        margin: 0.6rem 0 !important;
    }

    /* File uploader padding a bit smaller */
    section[data-testid="stFileUploadDropzone"] {
        padding: 0.35rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Configure HeyGen client
# -------------------------------------------------------------------

heygen_client.HEYGEN_API_KEY = st.secrets.get("HEYGEN_API_KEY", None)

DEFAULT_HEYGEN_AVATAR_ID = st.secrets.get("HEYGEN_DEFAULT_AVATAR_ID", "")
DEFAULT_HEYGEN_VOICE_ID = st.secrets.get("HEYGEN_DEFAULT_VOICE_ID", "")

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
            st.markdown(
                "\n".join(f"- {item}" for item in guide.required_materials_and_equipment)
            )

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
                st.markdown(
                    f"**Estimated Time:** {section.estimated_time_minutes} minutes"
                )

            if section.learning_objectives:
                st.markdown("**Learning Objectives**")
                st.markdown(
                    "\n".join(f"- {obj}" for obj in section.learning_objectives)
                )

            if section.instructional_steps:
                st.markdown("**Instructional Steps:**")
                st.markdown(
                    "\n".join(f"- {step}" for step in section.instructional_steps)
                )

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
        title = step.title or f"Step {step.step_number}"
        st.markdown(f"### Step {step.step_number}: {title}")
        if step.action:
            st.markdown(step.action)
        if step.notes:
            notes_text = step.notes.strip()
            if notes_text.upper().startswith("NOTE:") or notes_text.upper().startswith(
                "TIP:"
            ):
                st.markdown(f"> {notes_text}")
            else:
                st.markdown(f"> **NOTE:** {notes_text}")


# -------------------------------------------------------------------
# App layout & state
# -------------------------------------------------------------------

st.title("Training Class Generator")
st.write(
    "Upload training documents, audio, and/or handwritten notes to generate a "
    "class outline, instructor guide, video script, and quick reference guide."
)

# Initialize session state containers
st.session_state.setdefault("generated_package", None)
st.session_state.setdefault("combined_text", "")
st.session_state.setdefault("tts_payload", None)
st.session_state.setdefault("handwritten_notes_text", "")
st.session_state.setdefault("heygen_video_id", None)
st.session_state.setdefault("heygen_video_status", None)
st.session_state.setdefault("heygen_video_url", None)

# -------------------------------------------------------------------
# Inputs – 2-column layout
# -------------------------------------------------------------------

st.markdown("### 1. Course setup and sources")

# Row 1: Course details (left) + training docs (right)
col_course, col_docs = st.columns([1.1, 1.9])

with col_course:
    st.subheader("Course details")
    course_title = st.text_input("Course Title", value="", key="course_title_input")

    class_type = st.selectbox(
        "Class Type",
        ["Full Class", "Short Video", "Quick Reference Only"],
        key="class_type_select",
    )

with col_docs:
    st.subheader("Training documents")
    st.caption(
        "Upload slide decks, design docs, reference guides, or other written "
        "materials to use as the main source."
    )
    document_uploads = st.file_uploader(
        "Training/source documents (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="document_uploads",
    )

st.divider()

# Row 2: Handwritten notes (left) + audio + generate (right)
col_notes, col_audio = st.columns([1.8, 1.2])

with col_notes:
    st.subheader("Handwritten notes (optional)")
    st.caption(
        "Upload photos or screenshots of handwritten notes. The app will read them, "
        "let you edit the text, and include it with the other sources."
    )

    note_images = st.file_uploader(
        "Note images (JPG, PNG, HEIC, WEBP)",
        type=["jpg", "jpeg", "png", "heic", "webp"],
        accept_multiple_files=True,
        key="handwritten_images",
    )

    notes_btn_col, notes_clear_col = st.columns(2)

    with notes_btn_col:
        if note_images and st.button("Extract text from notes", use_container_width=True):
            with st.spinner("Reading notes from images..."):
                notes_text = extract_text_from_note_images(note_images)
            st.session_state.handwritten_notes_text = notes_text or ""
            st.success("Handwritten notes extracted. Review below.")

    with notes_clear_col:
        if st.session_state.handwritten_notes_text and st.button(
            "Clear notes", use_container_width=True
        ):
            st.session_state.handwritten_notes_text = ""

    if st.session_state.handwritten_notes_text:
        st.markdown("**Handwritten notes (review & edit before generating):**")
        st.session_state.handwritten_notes_text = st.text_area(
            "Edit notes text",
            st.session_state.handwritten_notes_text,
            height=220,
        )
    else:
        st.caption(
            "After extracting notes, the recognized text will appear here so you can review and clean it up."
        )

with col_audio:
    st.subheader("Audio (optional)")
    st.caption(
        "Upload recordings of prior classes or walkthroughs. "
        "Transcripts will be folded into the source text."
    )
    audio_uploads = st.file_uploader(
        "Audio files (WAV, MP3, M4A)",
        type=["wav", "mp3", "m4a"],
        accept_multiple_files=True,
        key="audio_uploads",
    )

    st.markdown("")  # small spacer
    st.subheader("Generate")
    st.caption(
        "Use whatever sources you’ve provided: documents, audio transcripts, and handwritten notes."
    )
    generate_clicked = st.button(
        "Generate Training Package",
        type="primary",
        key="generate_package_button",
        use_container_width=True,
    )

# -------------------------------------------------------------------
# Generation flow
# -------------------------------------------------------------------

if generate_clicked:
    if not course_title:
        st.error("Please enter a course title.")
    else:
        # Treat extracted handwritten notes as a valid source too
        notes_text_present = bool(
            (st.session_state.get("handwritten_notes_text", "") or "").strip()
        )

        if not document_uploads and not audio_uploads and not notes_text_present:
            st.error(
                "Please upload at least one document, audio file, or extract handwritten notes."
            )
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
                    combined_text_parts.append(
                        "[Audio Transcript]\n" + transcript_text
                    )

                full_text = "\n\n".join(combined_text_parts).strip()

                # Append handwritten notes if present
                notes_text = (
                    st.session_state.get("handwritten_notes_text", "") or ""
                ).strip()
                if notes_text:
                    if full_text:
                        full_text = (
                            full_text
                            + "\n\n=== Additional notes from instructor (handwritten) ===\n"
                            + notes_text
                        )
                    else:
                        full_text = (
                            "=== Additional notes from instructor (handwritten) ===\n"
                            + notes_text
                        )

                # If everything failed (no docs, no audio, no notes), fall back to a simple message
                if not full_text:
                    full_text = (
                        "No usable source text was extracted. "
                        "Create a generic but reasonable training package based only on the course title and class type."
                    )

                # Call generators
                outline = generate_class_outline(full_text, course_title, class_type)
                instructor_guide = generate_instructor_guide(
                    full_text, course_title, class_type
                )
                video_script = generate_video_script(
                    full_text, course_title, class_type
                )
                quick_reference = generate_quick_reference(
                    full_text, course_title, class_type
                )

                # Store in session_state
                st.session_state.generated_package = {
                    "outline": outline,
                    "instructor_guide": instructor_guide,
                    "video_script": video_script,
                    "quick_reference": quick_reference,
                }
                st.session_state.combined_text = full_text
                st.session_state.tts_payload = None

                # Reset HeyGen state on new generation
                st.session_state.heygen_video_id = None
                st.session_state.heygen_video_status = None
                st.session_state.heygen_video_url = None

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

        # ---------------- HeyGen integration ----------------
        st.markdown("---")
        st.subheader("HeyGen Avatar Video")

        # Editable script to send to HeyGen (default: markdown representation of video script)
        heygen_script_default = video_md or ""
        heygen_script_text = st.text_area(
            "Script to send to HeyGen (edit as needed before generating)",
            value=heygen_script_default,
            height=250,
        )

        bg_color = st.text_input("Background color (hex)", "#FFFFFF")

        col_hg_btn, col_hg_info = st.columns([1, 2])
        with col_hg_btn:
            generate_heygen_clicked = st.button(
                "Generate HeyGen Video",
                key="generate_heygen_video_button",
                use_container_width=True,
            )
        with col_hg_info:
            st.caption(
                "Uses the default HeyGen avatar and voice IDs configured in Streamlit secrets."
            )

        if generate_heygen_clicked:
            if not heygen_script_text.strip():
                st.error("No script text to send to HeyGen.")
            elif not heygen_client.HEYGEN_API_KEY:
                st.error(
                    "HEYGEN_API_KEY is not configured. Add it to st.secrets['HEYGEN_API_KEY']."
                )
            elif not DEFAULT_HEYGEN_AVATAR_ID or not DEFAULT_HEYGEN_VOICE_ID:
                st.error(
                    "Default HeyGen avatar or voice ID is not configured. "
                    "Add HEYGEN_DEFAULT_AVATAR_ID and HEYGEN_DEFAULT_VOICE_ID to st.secrets."
                )
            else:
                try:
                    with st.spinner("Submitting script to HeyGen..."):
                        video_id = heygen_client.create_avatar_video(
                            script_text=heygen_script_text,
                            avatar_id=DEFAULT_HEYGEN_AVATAR_ID,
                            voice_id=DEFAULT_HEYGEN_VOICE_ID,
                            test=False,
                            background_color=bg_color,
                        )
                        st.session_state.heygen_video_id = video_id

                    with st.spinner("Waiting for HeyGen to render the video..."):
                        status_data = heygen_client.wait_for_video(video_id)

                    data = status_data.get("data", status_data)
                    status = data.get("status")
                    video_url = data.get("video_url") or data.get("video_url_caption")

                    st.session_state.heygen_video_status = status
                    st.session_state.heygen_video_url = video_url

                    st.success(f"HeyGen video status: {status}")
                    if status == "completed" and video_url:
                        st.video(video_url)
                        st.text_input("Video URL", value=video_url)
                    else:
                        st.warning(
                            "Video did not complete successfully. Check the HeyGen dashboard for details."
                        )
                except heygen_client.HeyGenError as e:
                    st.error(f"HeyGen error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error while generating HeyGen video: {e}")

        # Show last HeyGen result if available
        if st.session_state.heygen_video_id:
            st.markdown("##### Last HeyGen Request")
            st.write(f"Video ID: `{st.session_state.heygen_video_id}`")
            if st.session_state.heygen_video_status:
                st.write(f"Status: **{st.session_state.heygen_video_status}**")
            if st.session_state.heygen_video_url:
                st.video(st.session_state.heygen_video_url)
                st.text_input(
                    "Video URL",
                    value=st.session_state.heygen_video_url,
                    key="heygen_video_url_display",
                )

        st.markdown("---")

        # ---------------- Existing TTS integration ----------------
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
                st.audio(payload, format="audio/wav")
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
    st.info(
        "Upload documents and/or audio, enter a title, optionally extract handwritten notes, "
        "and click **Generate Training Package** to begin."
    )
