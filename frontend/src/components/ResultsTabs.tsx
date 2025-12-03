import React, { useState } from 'react'
import type {
  ClassOutline,
  InstructorGuide,
  VideoScript,
  QuickReferenceGuide,
} from '../api/types'
import { artifactToMarkdown, copyToClipboard, downloadMarkdown } from '../utils/markdown'

const tabs = ['Outline', 'Instructor Guide', 'Video Script', 'Quick Reference'] as const

export type ArtifactData = {
  outline?: ClassOutline
  instructorGuide?: InstructorGuide
  videoScript?: VideoScript
  quickReference?: QuickReferenceGuide
}

export function ResultsTabs({ data }: { data: ArtifactData }) {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>('Outline')

  const renderContent = () => {
    switch (activeTab) {
      case 'Outline':
        return data.outline ? renderOutline(data.outline) : <p className="muted">No outline yet.</p>
      case 'Instructor Guide':
        return data.instructorGuide ? renderInstructor(data.instructorGuide) : <p className="muted">No instructor guide yet.</p>
      case 'Video Script':
        return data.videoScript ? renderVideo(data.videoScript) : <p className="muted">No video script yet.</p>
      case 'Quick Reference':
        return data.quickReference ? renderQuickRef(data.quickReference) : <p className="muted">No quick reference yet.</p>
      default:
        return null
    }
  }

  const currentMarkdown = (() => {
    switch (activeTab) {
      case 'Outline':
        return data.outline && artifactToMarkdown('outline', data.outline)
      case 'Instructor Guide':
        return data.instructorGuide && artifactToMarkdown('instructorGuide', data.instructorGuide)
      case 'Video Script':
        return data.videoScript && artifactToMarkdown('videoScript', data.videoScript)
      case 'Quick Reference':
        return data.quickReference && artifactToMarkdown('quickReference', data.quickReference)
      default:
        return ''
    }
  })()

  return (
    <div className="card results">
      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={tab === activeTab ? 'tab active' : 'tab'}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="tab-actions">
        <button onClick={() => copyToClipboard(currentMarkdown || '')}>Copy to Clipboard</button>
        <button onClick={() => downloadMarkdown(currentMarkdown || '', `${activeTab.replace(/\s+/g, '')}.md`)}>
          Download .md
        </button>
      </div>

      <div className="tab-body">{renderContent()}</div>
    </div>
  )
}

function renderOutline(outline: ClassOutline) {
  return (
    <div className="artifact">
      <h2 contentEditable suppressContentEditableWarning>
        {outline.title}
      </h2>
      {outline.sections.map((section, idx) => (
        <div key={idx} className="section" contentEditable suppressContentEditableWarning>
          <h3>
            {idx + 1}. {section.title}
          </h3>
          <p className="muted">Objectives:</p>
          <ul>
            {section.objectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
          {section.durationMinutes && <p className="muted">Duration: {section.durationMinutes} minutes</p>}
        </div>
      ))}
    </div>
  )
}

function renderInstructor(guide: InstructorGuide) {
  return (
    <div className="artifact">
      <h2 contentEditable suppressContentEditableWarning>{guide.courseTitle} - Instructor Guide</h2>
      {guide.sections.map((section, idx) => (
        <div key={idx} className="section" contentEditable suppressContentEditableWarning>
          <h3>
            {idx + 1}. {section.title}
          </h3>
          <p className="muted">Learning Objectives</p>
          <ul>
            {section.learningObjectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
          <p className="muted">Talking Points</p>
          <ul>
            {section.talkingPoints.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
          <p className="muted">Suggested Activities</p>
          <ul>
            {section.suggestedActivities.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
          {section.timingMinutes && <p className="muted">Timing: {section.timingMinutes} minutes</p>}
        </div>
      ))}
    </div>
  )
}

function renderVideo(video: VideoScript) {
  return (
    <div className="artifact">
      <h2 contentEditable suppressContentEditableWarning>{video.courseTitle} - Video Script</h2>
      {video.segments.map((segment, idx) => (
        <div key={idx} className="section" contentEditable suppressContentEditableWarning>
          <h3>
            Scene {idx + 1}: {segment.title}
          </h3>
          <p>
            <strong>Narration:</strong> {segment.narration}
          </p>
          <p>
            <strong>Screen Directions:</strong> {segment.screenDirections}
          </p>
          {segment.durationSeconds && <p className="muted">Duration: {segment.durationSeconds} seconds</p>}
        </div>
      ))}
    </div>
  )
}

function renderQuickRef(qrg: QuickReferenceGuide) {
  return (
    <div className="artifact">
      <h2 contentEditable suppressContentEditableWarning>{qrg.courseTitle} - Quick Reference Guide</h2>
      <ol>
        {qrg.steps.map((step) => (
          <li key={step.stepNumber} className="section" contentEditable suppressContentEditableWarning>
            <h3>
              Step {step.stepNumber}: {step.title}
            </h3>
            <p>
              <strong>Action:</strong> {step.action}
            </p>
            {step.notes && (
              <p>
                <strong>Notes:</strong> {step.notes}
              </p>
            )}
          </li>
        ))}
      </ol>
    </div>
  )
}
