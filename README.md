# Training Class Generator

A single Streamlit app that turns uploaded training materials into outlines, instructor guides, video scripts, and quick reference guides. Document extraction, LLM generation, speech-to-text, and text-to-speech are currently stubbed to make it easy to wire in real services later.

## Setup

1. (Optional) Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run

Start the Streamlit app:

```bash
streamlit run app.py
```

## Notes

- Upload PDF, DOCX, or TXT files plus optional audio (WAV, MP3, M4A) directly in the Streamlit UI.
- Content extraction, LLM outputs, speech-to-text, and TTS are placeholder implementations ready for replacement with real services (e.g., OpenAI Whisper/TTS).
- Generated artifacts are displayed in tabs and can be downloaded as Markdown files. TTS audio download buttons return stub audio bytes for now.
