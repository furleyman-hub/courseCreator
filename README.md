# Training Class Generator

A single Streamlit app that turns uploaded training materials into outlines, instructor guides, video scripts, and quick reference guides. You can generate outputs from documents, audio, or a mix of both. Document extraction uses pdfplumber/python-docx, while LLM generation, speech-to-text, and text-to-speech use the OpenAI API.

## Setup

1. (Optional) Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Provide your OpenAI API key via **either**:
   - `st.secrets["OPENAI_API_KEY"]` (recommended for Streamlit Cloud)
   - `OPENAI_API_KEY` environment variable

## Run

Start the Streamlit app:

```bash
streamlit run app.py
```

## Notes

- Upload PDF, DOCX, or TXT files plus optional audio (WAV, MP3, M4A) directly in the Streamlit UI.
- Document text extraction runs locally (PDF via pdfplumber, DOCX via python-docx, TXT direct read).
- LLM outputs, speech-to-text, and TTS use the OpenAI API.
- Generated artifacts are displayed in tabs and can be downloaded as Markdown files. Narration audio is generated per video segment for download.
