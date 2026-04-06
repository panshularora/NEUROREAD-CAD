"""Repository for ChildLearner: get or create, update after session."""
from __future__ import annotations

import json
from app.database import SessionLocal
from app.models.child_learner import ChildLearner


def get_or_create_learner(child_id: str, age: int = 6) -> ChildLearner:
    db = SessionLocal()
    try:
        learner = db.query(ChildLearner).filter(ChildLearner.child_id == child_id).first()
        if learner:
            return learner
        learner = ChildLearner(child_id=child_id, age=age)
        db.add(learner)
        db.commit()
        db.refresh(learner)
        return learner
    finally:
        db.close()


def update_learner_after_session(
    child_id: str,
    *,
    learning_level: int | None = None,
    error_patterns: dict | None = None,
    progress_metrics: dict | None = None,
    xp_delta: int = 0,
) -> None:
    db = SessionLocal()
    try:
        learner = db.query(ChildLearner).filter(ChildLearner.child_id == child_id).first()
        if not learner:
            return
        if learning_level is not None:
            learner.learning_level = learning_level
        if error_patterns is not None:
            learner.error_patterns = json.dumps(error_patterns)
        if progress_metrics is not None:
            learner.progress_metrics = json.dumps(progress_metrics)
        if xp_delta:
            learner.total_xp = (learner.total_xp or 0) + xp_delta
        db.commit()
    finally:
        db.close()
