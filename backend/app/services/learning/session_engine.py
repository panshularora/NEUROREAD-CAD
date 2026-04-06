"""
Learning session engine: start session, get next exercise, submit response.

Flow:
1. POST /session/start → create session, return session_id and first exercise (or just first exercise).
2. GET /exercise/next → return next exercise based on session state and adaptive logic.
3. POST /response/submit → record answer, update error patterns / level, return feedback + next exercise or completion.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from app.services.learning.adaptive_engine import (
    parse_error_patterns,
    parse_progress_metrics,
    record_confusion_error,
    get_primary_confusion_focus,
    compute_next_difficulty,
    get_recommendations,
)
from app.services.learning.content_engine import (
    get_letters_for_drill,
    get_words_for_spelling,
    get_sentences_for_reading,
    get_comprehension_question_set,
)

# In-memory session store (replace with Redis in production for multi-instance)
_sessions: Dict[str, Dict[str, Any]] = {}


def start_session(
    child_id: str,
    learning_level: int,
    error_patterns_raw: str,
    progress_metrics_raw: str,
    age: int = 6,
) -> Dict[str, Any]:
    """
    Start a new learning session. Returns session_id and first exercise.
    """
    session_id = str(uuid.uuid4())
    error_patterns = parse_error_patterns(error_patterns_raw)
    progress_metrics = parse_progress_metrics(progress_metrics_raw)
    focus = get_primary_confusion_focus(error_patterns)

    _sessions[session_id] = {
        "child_id": child_id,
        "learning_level": learning_level,
        "error_patterns": error_patterns,
        "progress_metrics": progress_metrics,
        "age": age,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "exercise_index": 0,
        "exercise_history": [],
        "recent_successes": 0,
        "recent_attempts": 0,
    }

    # First exercise: pick module by round-robin or weight (here: phonics first for demo)
    first = _next_exercise(session_id, focus, learning_level, error_patterns)
    return {
        "session_id": session_id,
        "learning_level": learning_level,
        "exercise": first,
        "started_at": _sessions[session_id]["started_at"],
    }


def _next_exercise(
    session_id: str,
    focus: Optional[str],
    learning_level: int,
    error_patterns: Dict[str, float],
) -> Dict[str, Any]:
    """Generate next exercise (phonics, spelling, comprehension, or reading)."""
    session = _sessions.get(session_id)
    if not session:
        return {"type": "complete", "message": "Session ended."}

    idx = session["exercise_index"]
    # Rotate: 0=phonics, 1=spelling, 2=comprehension, 3=reading
    mod = ["phonics", "spelling", "comprehension", "reading"][idx % 4]

    if mod == "phonics":
        letters = get_letters_for_drill(focus, count=5)
        return {
            "type": "phonics",
            "exercise_id": f"phonics_{uuid.uuid4().hex[:8]}",
            "task": "letter_sound",
            "letters": letters,
            "instruction": "Tap each letter to hear its sound.",
        }
    if mod == "spelling":
        words = get_words_for_spelling(learning_level, count=1)
        if not words:
            return {"type": "complete", "message": "No more spelling words."}
        return {
            "type": "spelling",
            "exercise_id": f"spelling_{uuid.uuid4().hex[:8]}",
            "word": words[0],
            "scrambled": _scramble(words[0]),
            "instruction": "Drag letters to spell the word.",
        }
    if mod == "comprehension":
        questions = get_comprehension_question_set(learning_level)
        if not questions:
            return {"type": "complete", "message": "No more questions."}
        q = questions[0]
        return {
            "type": "comprehension",
            "exercise_id": f"comp_{uuid.uuid4().hex[:8]}",
            "question": q["question"],
            "options": q["options"],
            "correct_index": q["correct"],
            "instruction": "Choose the best answer.",
        }
    # reading
    sentences = get_sentences_for_reading(learning_level, count=1)
    if not sentences:
        return {"type": "complete", "message": "No more reading."}
    return {
        "type": "reading",
        "exercise_id": f"reading_{uuid.uuid4().hex[:8]}",
        "sentence": sentences[0],
        "instruction": "Read aloud. Tap a word to hear it.",
    }


def _scramble(word: str) -> str:
    import random
    letters = list(word)
    random.shuffle(letters)
    return "".join(letters)


def submit_response(
    session_id: str,
    exercise_id: str,
    response: Any,
    *,
    is_correct: bool,
    expected: Optional[str] = None,
    actual: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Submit user response. expected/actual used for letter confusion (e.g. expected 'b', actual 'd').
    Returns feedback, XP delta, updated session state, and next exercise or completion.
    """
    session = _sessions.get(session_id)
    if not session:
        return {"error": "Session not found", "next": None}

    session["recent_attempts"] += 1
    if is_correct:
        session["recent_successes"] += 1

    # Update error patterns for confusion (e.g. spelling wrong letter)
    if expected and actual and expected != actual and len(expected) == 1 and len(actual) == 1:
        session["error_patterns"] = record_confusion_error(
            session["error_patterns"],
            expected.lower(),
            actual.lower(),
        )

    # XP and completion
    xp_delta = 10 if is_correct else 2
    session["exercise_history"].append({
        "exercise_id": exercise_id,
        "correct": is_correct,
        "xp": xp_delta,
    })
    session["exercise_index"] += 1

    # Next exercise or end
    focus = get_primary_confusion_focus(session["error_patterns"])
    next_ex = _next_exercise(
        session_id,
        focus,
        session["learning_level"],
        session["error_patterns"],
    )

    # Optionally adjust learning_level for next time (persist in DB elsewhere)
    new_level = compute_next_difficulty(
        session["learning_level"],
        session["recent_successes"] / max(1, session["recent_attempts"]),
        session["recent_attempts"],
    )
    session["learning_level"] = new_level

    return {
        "correct": is_correct,
        "xp_delta": xp_delta,
        "message": "Great job!" if is_correct else "Keep trying!",
        "next_exercise": next_ex if next_ex.get("type") != "complete" else None,
        "session_ended": next_ex.get("type") == "complete",
        "recommendations": get_recommendations(
            session["error_patterns"],
            session["progress_metrics"],
            new_level,
        ) if next_ex.get("type") == "complete" else None,
        "child_id": session["child_id"],
        "learning_level": new_level,
        "error_patterns": session["error_patterns"],
    }


def get_next_exercise(session_id: str) -> Dict[str, Any]:
    """GET /exercise/next: return next exercise without submitting (e.g. skip)."""
    session = _sessions.get(session_id)
    if not session:
        return {"error": "Session not found", "exercise": None}
    focus = get_primary_confusion_focus(session["error_patterns"])
    return {
        "exercise": _next_exercise(
            session_id,
            focus,
            session["learning_level"],
            session["error_patterns"],
        ),
    }
