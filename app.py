"""Streamlit app for generating training packages from documents and audio."""

from __future__ import annotations

import streamlit as st

from notes_ocr import extract_text_from_note_images

from generator import (
    ClassOutline,
    BatchProcessor,
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
    parse_document_to_chunks,
    synthesize_chunks,
    chunks_to_zip,
    OPENAI_TTS_VOICES,
    OPENAI_TTS_VOICES_HD_COMPATIBLE,
    TTS_MODEL,
    TTS_MODEL_HD,
)

import heygen_client

# -------------------------------------------------------------------
# Page config + CSS
# -------------------------------------------------------------------

st.set_page_config(page_title="Training Class Generator", layout="wide")

st.markdown(
    """
<style>
    .block-container {
        max-width: 900px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
    }
    div.stMarkdown, div.stTextInput, div.stSelectbox, div.stFileUploader,
    div[data-testid="stHorizontalBlock"] {
        margin-bottom: 0.3rem !important;
    }
    h2, h3 {
        margin-top: 0.6rem !important;
        margin-bottom: 0.3rem !important;
    }
    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }
    hr {
        margin: 0.6rem 0 !important;
    }
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

try:
    heygen_client.HEYGEN_API_KEY = st.secrets.get("HEYGEN_API_KEY", None)
    DEFAULT_HEYGEN_AVATAR_ID = st.secrets.get("HEYGEN_DEFAULT_AVATAR_ID", "")
    DEFAULT_HEYGEN_VOICE_ID = st.secrets.get("HEYGEN_DEFAULT_VOICE_ID", "")
except FileNotFoundError:
    heygen_client.HEYGEN_API_KEY = None
    DEFAULT_HEYGEN_AVATAR_ID = ""
    DEFAULT_HEYGEN_VOICE_ID = ""
except Exception:
    heygen_client.HEYGEN_API_KEY = None
    DEFAULT_HEYGEN_AVATAR_ID = ""
    DEFAULT_HEYGEN_VOICE_ID = ""

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
    if guide.training_plan_and_goals:
        st.subheader("Training plan and goals")
        st.write(guide.training_plan_and_goals)
    if guide.target_audience:
        st.subheader("Target audience")
        st.write(guide.target_audience)
    if guide.prerequisites:
        st.subheader("Prerequisites")
        st.write(guide.prerequisites)
    if guide.office365_status:
        st.subheader("Office 365 status")
        st.write(guide.office365_status)
    if guide.learning_objectives:
        st.subheader("Learning objectives")
        st.markdown("By the end of the session, participants will be able to:")
        st.markdown("\n".join(f"1. {obj}" for obj in guide.learning_objectives))
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
    if guide.class_type:
        st.subheader("Type of class")
        st.write(guide.class_type)
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
        title = step.title or f"Step {step.step_number}"
        st.markdown(f"### Step {step.step_number}: {title}")
        if step.action:
            st.markdown(step.action)
        if step.notes:
            notes_text = step.notes.strip()
            if notes_text.upper().startswith("NOTE:") or notes_text.upper().startswith("TIP:"):
                st.markdown(f"> {notes_text}")
            else:
                st.markdown(f"> **NOTE:** {notes_text}")


def _build_speakable_narration(script: VideoScript) -> str:
    if not script or not getattr(script, "segments", None):
        return ""
    chunks: list[str] = []
    for segment in script.segments:
        if segment.narration:
            text = segment.narration.strip()
            if text:
                chunks.append(text)
    return "\n\n".join(chunks).strip()


# -------------------------------------------------------------------
# Shared TTS settings widget (reused in both modes)
# -------------------------------------------------------------------

def _tts_settings_widgets(key_prefix: str) -> tuple[str, str]:
    """Render voice + model selectors; return (voice_display, model).

    Widget keys use an 'oai2_' infix to avoid conflicts with stale Streamlit
    session state from previous versions of this app.
    """
    col_model, col_voice = st.columns([1, 2])
    with col_model:
        model_choice = st.radio(
            "TTS Quality",
            ["Standard (fast, style support)", "HD (highest quality)"],
            index=0,
            key=f"{key_prefix}_oai2_model",
            help=(
                "Standard uses gpt-4o-mini-tts — supports speaking-style instructions "
                "and all 13 voices. HD uses tts-1-hd — highest audio quality, "
                "9 voices supported."
            ),
        )
    model = TTS_MODEL if model_choice == "Standard (fast, style support)" else TTS_MODEL_HD
    # HD model only supports the 9 core voices; Standard supports all 13
    available_voices = OPENAI_TTS_VOICES if model == TTS_MODEL else OPENAI_TTS_VOICES_HD_COMPATIBLE
    default_voice = "nova"
    default_idx = available_voices.index(default_voice) if default_voice in available_voices else 0
    with col_voice:
        voice = st.selectbox(
            "Voice",
            available_voices,
            index=default_idx,
            key=f"{key_prefix}_oai2_voice_{model}",
            help=(
                "Standard model: 13 voices including marin and cedar (OpenAI's recommended). "
                "HD model: 9 voices."
            ),
        )
    return voice, model


# -------------------------------------------------------------------
# App layout & state
# -------------------------------------------------------------------

mode = st.sidebar.radio(
    "App Mode",
    [
        "Interactive (Single Class)",
        "Batch Processing (CSV)",
        "TTS: Script to Audio",
    ],
)

# ===================================================================
# MODE: Batch Processing
# ===================================================================

if mode == "Batch Processing (CSV)":
    st.title("Batch Class Generation")
    st.markdown("Upload a CSV file to generate multiple training packages at once.")

    with st.expander("CSV Format Requirements", expanded=False):
        st.markdown(
            """
            The CSV must have the following headers:
            - **#**: Class number
            - **video_file**: Filename of the source video
            - **est_duration**: Estimated duration (e.g. \"5 mins\")
            - **brief_description**: Content summary used for generation
            """
        )

    uploaded_csv = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_csv:
        if st.button("Process Batch", type="primary"):
            processor = BatchProcessor()
            try:
                rows = processor.parse_csv(uploaded_csv)
                st.info(f"Loaded {len(rows)} classes from CSV. Starting generation...")

                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def update_progress(p, text):
                    progress_bar.progress(p)
                    status_text.text(text)

                zip_bytes = processor.process_batch(rows, progress_callback=update_progress)

                status_text.text("Batch processing complete!")
                st.success("All classes generated successfully.")

                st.download_button(
                    label="Download All Classes (.zip)",
                    data=zip_bytes,
                    file_name="batch_classes.zip",
                    mime="application/zip",
                )

            except Exception as e:
                st.error(str(e))

    st.stop()

# ===================================================================
# MODE: TTS – Script to Audio
# ===================================================================

if mode == "TTS: Script to Audio":
    st.title("TTS: Script to Audio")
    st.write(
        "Upload a script file (.txt, .md, or .docx). "
        "The app will split it by blank lines and generate a separate audio file for each section."
    )

    # ── File upload ──────────────────────────────────────────────────
    script_file = st.file_uploader(
        "Upload script file",
        type=["txt", "md", "docx"],
        key="tts_script_upload",
    )

    st.markdown("### TTS Settings")

    # ── Voice + model ────────────────────────────────────────────────
    tts_voice, tts_model = _tts_settings_widgets("standalone_tts")

    # ── Optional style prompt ────────────────────────────────────────
    style_prompt = st.text_input(
        "Speaking style (optional)",
        value="",
        key="standalone_tts_style",
        placeholder='e.g. "Speak in a calm, professional tone at a moderate pace"',
        help=(
            "A natural-language instruction prepended to each chunk before synthesis. "
            "Leave blank for the voice's default style."
        ),
    )

    st.divider()

    # ── Convert button ───────────────────────────────────────────────
    convert_clicked = st.button(
        "Convert to Audio",
        type="primary",
        key="standalone_tts_convert",
        use_container_width=True,
        disabled=script_file is None,
    )

    if "standalone_tts_results" not in st.session_state:
        st.session_state.standalone_tts_results = None
        st.session_state.standalone_tts_chunks = []

    if convert_clicked and script_file is not None:
        with st.spinner("Parsing document…"):
            try:
                chunks = parse_document_to_chunks(script_file)
            except Exception as exc:
                st.error(f"Failed to parse document: {exc}")
                chunks = []

        if not chunks:
            st.warning("No text chunks found in the document. Make sure paragraphs are separated by blank lines.")
        else:
            st.info(f"Found **{len(chunks)}** text chunk(s). Synthesizing audio…")
            progress = st.progress(0.0)
            results: dict[str, bytes] = {}
            errors = []

            for i, chunk in enumerate(chunks, start=1):
                progress.progress(i / len(chunks), text=f"Synthesizing chunk {i} of {len(chunks)}…")
                filename = f"chunk_{i:03d}.mp3"
                try:
                    chunk_result = synthesize_chunks(
                        [chunk],
                        voice_display=tts_voice,
                        model=tts_model,
                        style_prompt=style_prompt,
                    )
                    # synthesize_chunks returns {filename: bytes}; check if synthesis failed
                    result_key, audio_bytes = next(iter(chunk_result.items()))
                    if result_key.endswith("_ERROR.txt"):
                        error_key = f"chunk_{i:03d}_ERROR.txt"
                        results[error_key] = audio_bytes
                        errors.append(error_key)
                    else:
                        results[filename] = audio_bytes
                except Exception as exc:
                    error_key = f"chunk_{i:03d}_ERROR.txt"
                    results[error_key] = (
                        f"Error synthesizing chunk {i}:\n{exc}\n\nText:\n{chunk}"
                    ).encode("utf-8")
                    errors.append(error_key)

            progress.empty()
            st.session_state.standalone_tts_results = results
            st.session_state.standalone_tts_chunks = chunks

            if errors:
                st.warning(f"{len(errors)} chunk(s) failed to synthesize. See error files below.")
            else:
                st.success(f"All {len(results)} audio files generated!")

    # ── Display results ──────────────────────────────────────────────
    if st.session_state.standalone_tts_results:
        results = st.session_state.standalone_tts_results
        chunks_text = st.session_state.standalone_tts_chunks

        st.markdown("### Audio Files")

        wav_files = {k: v for k, v in results.items() if k.endswith(".mp3")}
        err_files = {k: v for k, v in results.items() if not k.endswith(".mp3")}

        for idx, (filename, audio_bytes) in enumerate(wav_files.items(), start=1):
            chunk_num = idx - 1
            chunk_preview = (
                chunks_text[chunk_num][:120] + "…"
                if chunk_num < len(chunks_text) and len(chunks_text[chunk_num]) > 120
                else (chunks_text[chunk_num] if chunk_num < len(chunks_text) else "")
            )
            with st.expander(f"**{filename}** — {chunk_preview}", expanded=idx <= 5):
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    f"⬇ Download {filename}",
                    audio_bytes,
                    file_name=filename,
                    key=f"standalone_dl_{filename}",
                )

        if err_files:
            st.markdown("#### Errors")
            for fname, err_bytes in err_files.items():
                st.error(err_bytes.decode("utf-8", errors="replace"))

        if wav_files:
            zip_bytes = chunks_to_zip(wav_files)
            st.download_button(
                "⬇ Download All as ZIP",
                zip_bytes,
                file_name="tts_audio.zip",
                mime="application/zip",
                key="standalone_tts_zip",
            )

    st.stop()

# ===================================================================
# MODE: Interactive (Single Class)
# ===================================================================

st.title("Training Class Generator")
st.write(
    "Upload training documents, audio, and/or handwritten notes to generate a "
    "class outline, instructor guide, video script, and quick reference guide."
)

# Initialize session state
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
    st.markdown("")
    st.subheader("Generate")
    st.caption(
        "Use whatever sources you have provided: documents, audio transcripts, and handwritten notes."
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
        notes_text_present = bool(
            (st.session_state.get("handwritten_notes_text", "") or "").strip()
        )
        if not document_uploads and not audio_uploads and not notes_text_present:
            st.error(
                "Please upload at least one document, audio file, or extract handwritten notes."
            )
        else:
            with st.spinner("Generating training package..."):
                document_text = extract_text_from_files(document_uploads)
                transcript_text = transcribe_audio_files(audio_uploads)

                combined_text_parts = []
                if document_text:
                    combined_text_parts.append(document_text)
                if transcript_text:
                    combined_text_parts.append("[Audio Transcript]\n" + transcript_text)

                full_text = "\n\n".join(combined_text_parts).strip()

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

                if not full_text:
                    full_text = (
                        "No usable source text was extracted. "
                        "Create a generic but reasonable training package based only on the course title and class type."
                    )

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

    with tabs[0]:
        st.header("Class Outline")
        _render_outline(package["outline"])
        outline_md = outline_to_markdown(package["outline"])
        st.download_button(
            "Download Outline (.md)", outline_md, file_name="class_outline.md", key="download_outline"
        )

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

        # ── HeyGen integration (unchanged) ────────────────────────
        st.markdown("---")
        st.subheader("HeyGen Avatar Video")

        narration_default = _build_speakable_narration(package["video_script"])
        heygen_script_text = st.text_area(
            "Script to send to HeyGen (narration only by default – edit as needed)",
            value=narration_default,
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
                "For free-plan testing, only a short excerpt (≈3 minutes of speech) "
                "is sent to HeyGen. Uses default avatar and voice IDs from secrets."
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
                script_to_send = heygen_script_text.strip()
                max_words = 350
                words = script_to_send.split()
                if len(words) > max_words:
                    script_to_send = " ".join(words[:max_words])
                    st.warning(
                        f"Script is longer than free-plan limit. "
                        f"Only the first {max_words} words were sent to HeyGen "
                        f"to target a video under ~180 seconds."
                    )
                max_chars = 4800
                if len(script_to_send) > max_chars:
                    script_to_send = script_to_send[:max_chars]
                    st.warning(
                        f"Script text exceeded HeyGen limits. "
                        f"Only the first {max_chars} characters were sent."
                    )
                try:
                    with st.spinner("Submitting script to HeyGen..."):
                        video_id = heygen_client.create_avatar_video(
                            script_text=script_to_send,
                            avatar_id=DEFAULT_HEYGEN_AVATAR_ID,
                            voice_id=DEFAULT_HEYGEN_VOICE_ID,
                            test=False,
                            background_color=bg_color,
                        )
                        st.session_state.heygen_video_id = video_id
                        st.session_state.heygen_video_status = "submitted"
                        st.session_state.heygen_video_url = None
                    st.success(
                        f"HeyGen request submitted. Video ID: {st.session_state.heygen_video_id}"
                    )
                except heygen_client.HeyGenError as e:
                    st.error(f"HeyGen error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error while generating HeyGen video: {e}")

        if st.session_state.heygen_video_id:
            st.markdown("##### HeyGen Status")
            col_status_btn, col_status_info = st.columns([1, 2])
            with col_status_btn:
                refresh_status = st.button(
                    "Check HeyGen Status",
                    key="check_heygen_status_button",
                    use_container_width=True,
                )
            with col_status_info:
                st.caption(
                    "Click to refresh the status from HeyGen. "
                    "Processing may take a while depending on load."
                )
            if refresh_status:
                try:
                    status_data = heygen_client.get_video_status(
                        st.session_state.heygen_video_id
                    )
                    data = status_data.get("data", status_data)
                    status = data.get("status")
                    video_url = data.get("video_url") or data.get("video_url_caption")
                    st.session_state.heygen_video_status = status
                    st.session_state.heygen_video_url = video_url
                    st.success(f"Latest HeyGen status: {status}")
                except heygen_client.HeyGenError as e:
                    st.error(f"HeyGen error while checking status: {e}")
                except Exception as e:
                    st.error(f"Unexpected error while checking HeyGen status: {e}")

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

        # ── OpenAI TTS narration ──────────────────────────────────
        st.markdown("---")
        st.subheader("Narration Audio (OpenAI TTS)")

        tts_voice_course, tts_model_course = _tts_settings_widgets("course_tts")

        style_prompt_course = st.text_input(
            "Speaking style (optional)",
            value="",
            key="course_tts_style",
            placeholder='e.g. "Speak slowly and clearly with a warm, encouraging tone"',
            help="A natural-language style instruction prepended to each segment's narration.",
        )

        if st.button("Generate Narration Audio", key="generate_tts_button"):
            with st.spinner("Generating narration audio via OpenAI TTS..."):
                try:
                    from generator.openai_client import MissingOpenAIKeyError
                    st.session_state.tts_payload = synthesize_narration_audio(
                        package["video_script"],
                        voice_display=tts_voice_course,
                        model=tts_model_course,
                    )
                except MissingOpenAIKeyError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"TTS generation failed: {exc}")

        if st.session_state.tts_payload:
            wav_items = {
                k: v for k, v in st.session_state.tts_payload.items() if k.endswith(".mp3")
            }
            err_items = {
                k: v for k, v in st.session_state.tts_payload.items() if not k.endswith(".mp3")
            }
            if wav_items:
                st.info("Preview and download narration segments below.")
                for filename, payload in wav_items.items():
                    st.markdown(f"**{filename}**")
                    st.audio(payload, format="audio/mp3")
                    st.download_button(
                        f"Download {filename}",
                        payload,
                        file_name=filename,
                        key=f"download_tts_{filename}",
                    )
                if len(wav_items) > 1:
                    zip_bytes = chunks_to_zip(wav_items)
                    st.download_button(
                        "⬇ Download All Segments as ZIP",
                        zip_bytes,
                        file_name="narration_audio.zip",
                        mime="application/zip",
                        key="course_tts_zip",
                    )
            if err_items:
                for fname, err_bytes in err_items.items():
                    st.error(err_bytes.decode("utf-8", errors="replace"))

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

    with st.expander("Show combined source text used for generation"):
        st.write(st.session_state.combined_text or "No source text available.")
else:
    st.info(
        "Upload documents and/or audio, enter a title, optionally extract handwritten notes, "
        "and click **Generate Training Package** to begin."
    )
