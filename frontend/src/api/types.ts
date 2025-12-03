export type ClassOutlineSection = {
  title: string
  objectives: string[]
  durationMinutes?: number
}

export type ClassOutline = {
  title: string
  sections: ClassOutlineSection[]
}

export type InstructorGuideSection = {
  title: string
  learningObjectives: string[]
  talkingPoints: string[]
  suggestedActivities: string[]
  timingMinutes?: number
}

export type InstructorGuide = {
  courseTitle: string
  sections: InstructorGuideSection[]
}

export type VideoScriptSegment = {
  title: string
  narration: string
  screenDirections: string
  durationSeconds?: number
}

export type VideoScript = {
  courseTitle: string
  segments: VideoScriptSegment[]
}

export type QuickReferenceStep = {
  stepNumber: number
  title: string
  action: string
  notes?: string
}

export type QuickReferenceGuide = {
  courseTitle: string
  steps: QuickReferenceStep[]
}

export type GeneratePayload = {
  extractedText: string
  courseTitle: string
  classType: string
}

export type GenerateResponse = {
  classOutline: ClassOutline
  instructorGuide: InstructorGuide
  videoScript: VideoScript
  quickReferenceGuide: QuickReferenceGuide
}
