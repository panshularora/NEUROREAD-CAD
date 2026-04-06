"""
Learning session API: start session, get next exercise, submit response.

REST design:
- POST /session/start   → start session, return session_id + first exercise
- GET  /exercise/next   → get next exercise (e.g. after page refresh)
- POST /response/submit → submit answer, return feedback + next exercise or completion
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.learning.session_engine import (
    start_session as engine_start,
    get_next_exercise,
    submit_response as engine_submit,
)
from app.services.learning.learner_repo import get_or_create_learner, update_learner_after_session

router = APIRouter()


class SessionStartRequest(BaseModel):
    child_id: str = Field(..., min_length=1)
    age: int = Field(default=6, ge=4, le=10)


@router.post("/session/start")
def session_start(req: SessionStartRequest):
    """Start a new learning session. Returns session_id and first exercise."""
    learner = get_or_create_learner(req.child_id, req.age)
    learning_level = learner.learning_level or 1
    error_patterns_raw = learner.error_patterns or "{}"
    progress_metrics_raw = learner.progress_metrics or "{}"
    result = engine_start(
        child_id=req.child_id,
        learning_level=learning_level,
        error_patterns_raw=error_patterns_raw,
        progress_metrics_raw=progress_metrics_raw,
        age=learner.age or req.age,
    )
    result["child_id"] = req.child_id
    return result


class ExerciseNextRequest(BaseModel):
    session_id: str = Field(..., min_length=1)


@router.get("/exercise/next")
def exercise_next(session_id: str):
    """Get the next exercise in the current session (e.g. for refresh or skip)."""
    result = get_next_exercise(session_id)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


class SubmitResponseRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    exercise_id: str = Field(..., min_length=1)
    is_correct: bool
    response: str | int | list | None = None  # raw answer for logging
    expected: str | None = None  # e.g. letter "b"
    actual: str | None = None    # e.g. letter "d" (what user wrote/said)


@router.post("/response/submit")
def response_submit(req: SubmitResponseRequest):
    """Submit user response. Returns feedback, XP, and next exercise or completion."""
    result = engine_submit(
        session_id=req.session_id,
        exercise_id=req.exercise_id,
        response=req.response,
        is_correct=req.is_correct,
        expected=req.expected,
        actual=req.actual,
    )
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    # Persist updated learner state (level, error patterns, XP)
    child_id = result.get("child_id")
    if child_id:
        update_learner_after_session(
            child_id,
            learning_level=result.get("learning_level"),
            error_patterns=result.get("error_patterns"),
            xp_delta=result.get("xp_delta", 0),
        )
    return result


@router.get("/progress")
def learning_progress(child_id: str):
    """Get learning progress for a child (XP, level, metrics, recommendations)."""
    learner = get_or_create_learner(child_id)
    from app.services.learning.adaptive_engine import (
        parse_error_patterns,
        parse_progress_metrics,
        get_recommendations,
    )
    error_patterns = parse_error_patterns(learner.error_patterns)
    progress_metrics = parse_progress_metrics(learner.progress_metrics)
    recs = get_recommendations(
        error_patterns,
        progress_metrics,
        learner.learning_level or 1,
    )
    return {
        "child_id": learner.child_id,
        "age": learner.age,
        "learning_level": learner.learning_level,
        "total_xp": learner.total_xp or 0,
        "streak_days": learner.streak_days or 0,
        "error_patterns": error_patterns,
        "progress_metrics": progress_metrics,
        "recommendations": recs,
    }


@router.get("/recommendations")
def recommendations(child_id: str):
    """Get smart recommendations for this child (focus areas, tips)."""
    learner = get_or_create_learner(child_id)
    from app.services.learning.adaptive_engine import (
        parse_error_patterns,
        parse_progress_metrics,
        get_recommendations,
    )
    recs = get_recommendations(
        parse_error_patterns(learner.error_patterns),
        parse_progress_metrics(learner.progress_metrics),
        learner.learning_level or 1,
    )
    return {"child_id": child_id, "recommendations": recs}
