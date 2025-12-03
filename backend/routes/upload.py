from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from backend.services.extraction import extract_text_from_files, save_uploaded_files

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


@router.post("/upload")
async def upload_files(
    courseTitle: str = Form(...),
    classType: str = Form(...),
    files: List[UploadFile] = File(...),
):
    try:
        file_bytes = [await file.read() for file in files]
        file_names = [file.filename or "upload.bin" for file in files]
        saved_paths = save_uploaded_files(file_bytes, file_names, UPLOAD_DIR)
        extracted_text = extract_text_from_files(saved_paths)
        return {
            "courseTitle": courseTitle,
            "classType": classType,
            "files": file_names,
            "extractedText": extracted_text,
        }
    except Exception as exc:  # pragma: no cover - simple safety net
        return JSONResponse(status_code=500, content={"error": str(exc)})
