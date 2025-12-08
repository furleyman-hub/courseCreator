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
            st.markdown("\n".join(f"- {item}" for item in guide.class_checkl_
