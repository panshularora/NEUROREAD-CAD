from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.learning.learning_mode_api import LearningModeAPI

router = APIRouter()
api_instance = LearningModeAPI()

class SessionStartReq(BaseModel):
    child_id: str
    age: int = 6

@router.post("/learning/session/start_flow")
def start_session_flow(req: SessionStartReq):
    return api_instance.start_session({"child_id": req.child_id, "age": req.age})

class SubmitAnsReq(BaseModel):
    session_id: str
    answer: str
    response_time_ms: int

@router.post("/learning/response/submit_flow")
def submit_ans_flow(req: SubmitAnsReq):
    return api_instance.submit_answer(req.session_id, req.answer, req.response_time_ms)
