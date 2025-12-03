# Training Package Generator (Streamlit)

A single Streamlit app that ingests training materials and produces class outlines, instructor guides, video scripts, and quick reference guides. No separate backend or frontend servers are required.

## Setup

1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Set `OPENAI_API_KEY` in your environment to enable live ChatGPT generations. Without a key, structured fallbacks are returned.

## Running the App

```bash
streamlit run app.py
```

The UI runs entirely in Streamlit—upload documents, enter a course title, select the class type, optionally provide an OpenAI API key, and click **Generate Training Package**.

## Project Structure

- `app.py` – Streamlit UI and orchestration.
- `backend/models/types.py` – Pydantic models describing generated artifacts.
- `backend/services/llm.py` – ChatGPT-backed (or fallback) generators.
- `backend/services/extraction.py` – Stubbed text extraction helpers.
- `backend/services/pipeline.py` – Utilities to extract text and build artifacts.
- `backend/services/formatting.py` – Markdown formatting helpers for artifacts.

## Notes

- All processing happens locally in the Streamlit process—no HTTP calls are made beyond the optional OpenAI API.
- Replace `extract_text_from_files` in `backend/services/extraction.py` with real PDF/Docx parsing as needed.
