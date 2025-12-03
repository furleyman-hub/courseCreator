import React, { useState } from 'react'
import { uploadFiles, generatePackage } from './api/client'
import type { GenerateResponse } from './api/types'
import { UploadForm } from './components/UploadForm'
import { ResultsTabs } from './components/ResultsTabs'

function App() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [extractedText, setExtractedText] = useState<string>('')
  const [courseTitle, setCourseTitle] = useState<string>('')
  const [classType, setClassType] = useState<string>('')
  const [results, setResults] = useState<GenerateResponse | null>(null)

  const handleUploadAndGenerate = async (title: string, type: string, files: File[]) => {
    setLoading(true)
    setMessage(null)
    try {
      const uploadResponse = await uploadFiles(title, type, files)
      setExtractedText(uploadResponse.extractedText)
      setCourseTitle(title)
      setClassType(type)

      const generated = await generatePackage({
        extractedText: uploadResponse.extractedText,
        courseTitle: title,
        classType: type,
      })
      setResults(generated)
    } catch (error: any) {
      setMessage(error?.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <UploadForm onSubmit={handleUploadAndGenerate} loading={loading} />

      {message && <div className="error banner">{message}</div>}

      {extractedText && (
        <div className="card">
          <p className="eyebrow">Extracted Text (preview)</p>
          <p className="muted">We use this text to generate the training package.</p>
          <textarea readOnly value={extractedText} className="preview" />
        </div>
      )}

      {results && (
        <ResultsTabs
          data={{
            outline: results.classOutline,
            instructorGuide: results.instructorGuide,
            videoScript: results.videoScript,
            quickReference: results.quickReferenceGuide,
          }}
        />
      )}
    </div>
  )
}

export default App
