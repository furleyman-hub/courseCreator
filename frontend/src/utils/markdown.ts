import type { ClassOutline, InstructorGuide, VideoScript, QuickReferenceGuide } from '../api/types'

type ArtifactType = 'outline' | 'instructorGuide' | 'videoScript' | 'quickReference'

type ArtifactMap = {
  outline: ClassOutline
  instructorGuide: InstructorGuide
  videoScript: VideoScript
  quickReference: QuickReferenceGuide
}

export function artifactToMarkdown<T extends ArtifactType>(type: T, data: ArtifactMap[T]): string {
  switch (type) {
    case 'outline': {
      const outline = data as ClassOutline
      const sections = outline.sections
        .map(
          (section, idx) =>
            `## ${idx + 1}. ${section.title}\n` +
            (section.objectives.length
              ? `**Objectives:**\n${section.objectives.map((o) => `- ${o}`).join('\n')}\n`
              : '') +
            (section.durationMinutes ? `**Duration:** ${section.durationMinutes} minutes\n` : '')
        )
        .join('\n')
      return `# ${outline.title}\n\n${sections}`
    }
    case 'instructorGuide': {
      const guide = data as InstructorGuide
      const sections = guide.sections
        .map(
          (section, idx) =>
            `## ${idx + 1}. ${section.title}\n` +
            `**Learning Objectives**\n${section.learningObjectives.map((o) => `- ${o}`).join('\n')}\n` +
            `**Talking Points**\n${section.talkingPoints.map((o) => `- ${o}`).join('\n')}\n` +
            `**Suggested Activities**\n${section.suggestedActivities.map((o) => `- ${o}`).join('\n')}\n` +
            (section.timingMinutes ? `**Timing:** ${section.timingMinutes} minutes\n` : '')
        )
        .join('\n')
      return `# ${guide.courseTitle} - Instructor Guide\n\n${sections}`
    }
    case 'videoScript': {
      const script = data as VideoScript
      const segments = script.segments
        .map(
          (segment, idx) =>
            `## Scene ${idx + 1}: ${segment.title}\n` +
            `**Narration**\n${segment.narration}\n` +
            `**Screen Directions**\n${segment.screenDirections}\n` +
            (segment.durationSeconds ? `**Duration:** ${segment.durationSeconds} seconds\n` : '')
        )
        .join('\n')
      return `# ${script.courseTitle} - Video Script\n\n${segments}`
    }
    case 'quickReference': {
      const qrg = data as QuickReferenceGuide
      const steps = qrg.steps
        .map(
          (step) =>
            `${step.stepNumber}. ${step.title}\n` +
            `- Action: ${step.action}\n` +
            (step.notes ? `- Notes: ${step.notes}\n` : '')
        )
        .join('\n')
      return `# ${qrg.courseTitle} - Quick Reference Guide\n\n${steps}`
    }
    default:
      return ''
  }
}

export function downloadMarkdown(markdown: string, filename: string) {
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export async function copyToClipboard(markdown: string) {
  await navigator.clipboard.writeText(markdown)
}
