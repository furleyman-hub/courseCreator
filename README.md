# Training Class Generator

A full-stack demo that turns uploaded training materials into a generated training package. The backend uses FastAPI and exposes upload and generation endpoints with ChatGPT-powered generation (and safe fallbacks when no API key is provided). The frontend is a React + Vite single-page app that uploads documents, displays extracted text, and renders outline, instructor guide, video script, and quick reference results with copy/download actions.
A full-stack demo that turns uploaded training materials into a generated training package. The backend uses FastAPI and exposes upload and generation endpoints with stubbed LLM calls. The frontend is a React + Vite single-page app that uploads documents, displays extracted text, and renders outline, instructor guide, video script, and quick reference results with copy/download actions.

## Folder Structure
```
backend/
  main.py                # FastAPI entrypoint
  requirements.txt       # Backend dependencies
  routes/                # API route modules (upload, generate)
  services/              # Extraction + LLM helpers
  services/              # Extraction + LLM stubs
  models/                # Pydantic models
  uploads/               # Temporary upload storage
streamlit_app.py         # Streamlit UI that calls the FastAPI backend
frontend/
  index.html             # Vite entry HTML
  package.json           # Frontend dependencies and scripts
  tsconfig.json          # TypeScript config
  vite.config.ts         # Vite config
  src/                   # React source
    App.tsx              # Main SPA component
    main.tsx             # React entry
    index.css            # Styling
    api/                 # API client + types
    components/          # UI building blocks
    utils/               # Markdown helpers
```

## Setup

1. (Optional) Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key (optional for mocked responses):
   ```bash
   export OPENAI_API_KEY=your_key_here
   # optional: export OPENAI_MODEL=gpt-4o-mini  # override the default model
   ```
   > You can also send a one-off key from the Streamlit UI or in the `/api/generate` payload via `openaiApiKey`.
3. Run the API (default on port 8000):
2. Run the API (default on port 8000):
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Run

Start the Streamlit app:

```bash
streamlit run app.py
```

## Notes
- LLM calls use ChatGPT via the `openai` Python SDK. If no API key is provided, the backend falls back to the previous mock data.
- LLM calls are mocked via placeholder functions in `backend/services/llm.py`. Replace these with real API calls as needed.
- File text extraction is stubbed in `backend/services/extraction.py`; swap in real PDF/DOCX parsers for production use.
