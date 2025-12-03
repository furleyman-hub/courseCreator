from typing import List, Optional
from pydantic import BaseModel, Field


class ClassOutlineSection(BaseModel):
    title: str
    objectives: List[str] = Field(default_factory=list)
    durationMinutes: Optional[int] = None


class ClassOutline(BaseModel):
    title: str
    sections: List[ClassOutlineSection] = Field(default_factory=list)


class InstructorGuideSection(BaseModel):
    title: str
    learningObjectives: List[str] = Field(default_factory=list)
    talkingPoints: List[str] = Field(default_factory=list)
    suggestedActivities: List[str] = Field(default_factory=list)
    timingMinutes: Optional[int] = None


class InstructorGuide(BaseModel):
    courseTitle: str
    sections: List[InstructorGuideSection] = Field(default_factory=list)


class VideoScriptSegment(BaseModel):
    title: str
    narration: str
    screenDirections: str
    durationSeconds: Optional[int] = None


class VideoScript(BaseModel):
    courseTitle: str
    segments: List[VideoScriptSegment] = Field(default_factory=list)


class QuickReferenceStep(BaseModel):
    stepNumber: int
    title: str
    action: str
    notes: Optional[str] = None


class QuickReferenceGuide(BaseModel):
    courseTitle: str
    steps: List[QuickReferenceStep] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    extractedText: str
    courseTitle: str
    classType: str
    openaiApiKey: Optional[str] = Field(default=None, description="Optional per-request OpenAI API key")


class GenerateResponse(BaseModel):
    classOutline: ClassOutline
    instructorGuide: InstructorGuide
    videoScript: VideoScript
    quickReferenceGuide: QuickReferenceGuide
