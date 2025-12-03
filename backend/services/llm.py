from backend.models.types import (
    ClassOutline,
    ClassOutlineSection,
    InstructorGuide,
    InstructorGuideSection,
    QuickReferenceGuide,
    QuickReferenceStep,
    VideoScript,
    VideoScriptSegment,
)


def generate_class_outline(text: str, course_title: str) -> ClassOutline:
    # TODO: Swap with real LLM call
    sections = [
        ClassOutlineSection(
            title="Introduction",
            objectives=["Understand goals", "Set expectations"],
            durationMinutes=10,
        ),
        ClassOutlineSection(
            title="Core Concepts",
            objectives=["Learn the basics", "Review examples"],
            durationMinutes=30,
        ),
    ]
    return ClassOutline(title=course_title, sections=sections)


def generate_instructor_guide(text: str, course_title: str) -> InstructorGuide:
    sections = [
        InstructorGuideSection(
            title="Kickoff",
            learningObjectives=["Establish rapport", "Preview agenda"],
            talkingPoints=["Welcome participants", "Share outcomes"],
            suggestedActivities=["Icebreaker question"],
            timingMinutes=5,
        ),
        InstructorGuideSection(
            title="Hands-on Walkthrough",
            learningObjectives=["Practice workflow"],
            talkingPoints=["Demonstrate key steps", "Highlight pitfalls"],
            suggestedActivities=["Live demo", "Group exercise"],
            timingMinutes=25,
        ),
    ]
    return InstructorGuide(courseTitle=course_title, sections=sections)


def generate_video_script(text: str, course_title: str) -> VideoScript:
    segments = [
        VideoScriptSegment(
            title="Scene 1 - Overview",
            narration="Welcome to the training. In this lesson, we'll cover the essentials.",
            screenDirections="Show title slide, slow zoom, then fade to dashboard.",
            durationSeconds=45,
        ),
        VideoScriptSegment(
            title="Scene 2 - Doing the Work",
            narration="Click on 'Create' to start a new project and fill in the details.",
            screenDirections="Capture cursor clicking Create, highlight form fields, zoom on Save button.",
            durationSeconds=75,
        ),
    ]
    return VideoScript(courseTitle=course_title, segments=segments)


def generate_quick_reference(text: str, course_title: str) -> QuickReferenceGuide:
    steps = [
        QuickReferenceStep(
            stepNumber=1,
            title="Set Up",
            action="Open the application and sign in with your credentials.",
            notes="Use SSO when available.",
        ),
        QuickReferenceStep(
            stepNumber=2,
            title="Create Item",
            action="Click 'Create', enter required fields, and press Save.",
            notes="Fields marked * are mandatory.",
        ),
    ]
    return QuickReferenceGuide(courseTitle=course_title, steps=steps)
