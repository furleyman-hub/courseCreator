import type { GeneratePayload, GenerateResponse } from './types'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export async function uploadFiles(
  courseTitle: string,
  classType: string,
  files: File[]
): Promise<{ courseTitle: string; classType: string; files: string[]; extractedText: string }> {
  const formData = new FormData()
  formData.append('courseTitle', courseTitle)
  formData.append('classType', classType)
  files.forEach((file) => formData.append('files', file))

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    throw new Error('Upload failed')
  }

  return res.json()
}

export async function generatePackage(payload: GeneratePayload): Promise<GenerateResponse> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    throw new Error('Generation failed')
  }

  return res.json()
}
