# Training Package Generator

A full-stack demo that turns uploaded training materials into a generated training package. The backend uses FastAPI and exposes upload and generation endpoints with ChatGPT-powered generation (and safe fallbacks when no API key is provided). The frontend is a React + Vite single-page app that uploads documents, displays extracted text, and renders outline, instructor guide, video script, and quick reference results with copy/download actions.

## Folder Structure
```
backend/
  main.py                # FastAPI entrypoint
  requirements.txt       # Backend dependencies
  routes/                # API route modules (upload, generate)
  services/              # Extraction + LLM helpers
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

### Backend
1. Create a virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key (optional for mocked responses):
   ```bash
   export OPENAI_API_KEY=your_key_here
   # optional: export OPENAI_MODEL=gpt-4o-mini  # override the default model
   ```
   > You can also send a one-off key from the Streamlit UI or in the `/api/generate` payload via `openaiApiKey`.
3. Run the API (default on port 8000):
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Streamlit UI (alternative browser client)
1. Ensure the backend is running (default `http://localhost:8000`).
2. From the repo root, activate your backend virtualenv (or install the backend requirements globally) and start Streamlit:
   ```bash
   streamlit run streamlit_app.py
   ```
3. Open the provided local URL in your browser (e.g., `http://localhost:8501`). Use the sidebar to point to a different backend URL if needed.

### Frontend
1. Install dependencies (Node 18+ recommended):
   ```bash
   cd frontend
   npm install
   ```
2. Start the dev server (default on port 5173):
   ```bash
   npm run dev
   ```

### Connecting Frontend and Backend
- The frontend expects the backend at `http://localhost:8000/api`. Set `VITE_API_BASE` in a `.env` file in `frontend/` if you need a different URL.
- Start the backend first, then run the frontend and open `http://localhost:5173`.

## Usage
1. Enter a course title, choose a class type, and upload one or more files.
2. Click **Generate Training Package**. The app uploads files, shows extracted text, and displays generated artifacts in tabs.
3. Use **Copy to Clipboard** or **Download .md** to export each artifact.
4. If you prefer Streamlit, run `streamlit run streamlit_app.py` and use the browser UI it provides instead of the Vite SPA.

## Notes
- LLM calls use ChatGPT via the `openai` Python SDK. If no API key is provided, the backend falls back to the previous mock data.
- File text extraction is stubbed in `backend/services/extraction.py`; swap in real PDF/DOCX parsers for production use.
