# Training Package Generator

A full-stack demo that turns uploaded training materials into a generated training package. The backend uses FastAPI and exposes upload and generation endpoints with stubbed LLM calls. The frontend is a React + Vite single-page app that uploads documents, displays extracted text, and renders outline, instructor guide, video script, and quick reference results with copy/download actions.

## Folder Structure
```
backend/
  main.py                # FastAPI entrypoint
  requirements.txt       # Backend dependencies
  routes/                # API route modules (upload, generate)
  services/              # Extraction + LLM stubs
  models/                # Pydantic models
  uploads/               # Temporary upload storage
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
2. Run the API (default on port 8000):
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

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

## Notes
- LLM calls are mocked via placeholder functions in `backend/services/llm.py`. Replace these with real API calls as needed.
- File text extraction is stubbed in `backend/services/extraction.py`; swap in real PDF/DOCX parsers for production use.
