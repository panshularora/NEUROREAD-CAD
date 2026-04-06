from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.assistive.tts_service import generate_speech_audio

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    slow: bool = False


@router.post("/tts")
def generate_tts(request: TTSRequest):
    try:
        result = generate_speech_audio(request.text, slow=request.slow)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"audio_url": result.audio_url, "filename": result.filename}


# New path (keeps legacy `/tts` working too)
@router.post("/assistive/tts")
def generate_tts_assistive(request: TTSRequest):
    return generate_tts(request)