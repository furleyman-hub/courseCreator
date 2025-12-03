from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.models.types import GenerateRequest, GenerateResponse
from backend.services import llm

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_package(payload: GenerateRequest):
    try:
        outline = llm.generate_class_outline(payload.extractedText, payload.courseTitle)
        instructor = llm.generate_instructor_guide(payload.extractedText, payload.courseTitle)
        video = llm.generate_video_script(payload.extractedText, payload.courseTitle)
        qrg = llm.generate_quick_reference(payload.extractedText, payload.courseTitle)
        return GenerateResponse(
            classOutline=outline,
            instructorGuide=instructor,
            videoScript=video,
            quickReferenceGuide=qrg,
        )
    except Exception as exc:  # pragma: no cover - safety net
        return JSONResponse(status_code=500, content={"error": str(exc)})
