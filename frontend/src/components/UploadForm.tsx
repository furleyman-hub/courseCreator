import React, { useState } from 'react'

const classTypes = ['Full Class', 'Short Video', 'Quick Reference Only']

type Props = {
  onSubmit: (courseTitle: string, classType: string, files: File[]) => Promise<void>
  loading: boolean
}

export function UploadForm({ onSubmit, loading }: Props) {
  const [courseTitle, setCourseTitle] = useState('')
  const [classType, setClassType] = useState(classTypes[0])
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return
    setSelectedFiles(Array.from(event.target.files))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    if (!courseTitle.trim()) {
      setError('Please provide a course title.')
      return
    }
    if (selectedFiles.length === 0) {
      setError('Please choose at least one file.')
      return
    }
    try {
      await onSubmit(courseTitle, classType, selectedFiles)
    } catch (err: any) {
      setError(err?.message || 'Upload failed')
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="card-header">
        <div>
          <p className="eyebrow">Source Material</p>
          <h1>Upload training documents</h1>
          <p className="muted">
            Add PDFs, Word docs, or text files. We'll extract the text and create a training package.
          </p>
        </div>
        <button type="submit" className="primary" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Training Package'}
        </button>
      </div>

      <label className="field">
        <span>Course Title</span>
        <input
          type="text"
          value={courseTitle}
          onChange={(e) => setCourseTitle(e.target.value)}
          placeholder="e.g., Onboarding for New Sales Reps"
        />
      </label>

      <label className="field">
        <span>Class Type</span>
        <select value={classType} onChange={(e) => setClassType(e.target.value)}>
          {classTypes.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Upload Files</span>
        <input type="file" multiple onChange={handleFileChange} />
        {selectedFiles.length > 0 && <p className="muted">{selectedFiles.length} files selected</p>}
      </label>

      {error && <div className="error">{error}</div>}
    </form>
  )
}
