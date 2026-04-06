"""
Session Orchestrator

The unified intelligence coordinator.
WHY THIS ARCHITECTURE IS BETTER THAN THE OLD SESSION_ENGINE:
The old engine relied on a single discrete matrix and a raw success-rate percentage threshold (if >0.75, +1).
This orchestrator employs:
1. Bayesian Knowledge Tracing (BKT) to probabilistically track concept mastery over time instead of guess-and-check.
2. Item Response Theory (2PL) to calibrate ability mathematically against fluid difficulty, ignoring false negatives (slips).
3. SuperMemo-2 (SM-2) Spaced Repetition to inject forgotten items precisely when retention reaches decay (Ebbinghaus curve).
These systems together create a dynamic, true AI-tutoring system rather than a statically nested loop.
"""

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timezone

from app.services.learning.bkt_engine import SkillBelief, select_next_skill, load_child_beliefs
from app.services.learning.irt_scorer import estimate_ability_update, calibrate_item_difficulty, ability_to_level
from app.services.learning.content_generator import EXERCISE_SCHEMA, generate_exercise
from app.services.learning.spaced_repetition import ExerciseRecord, compute_quality, update_schedule, get_review_priority

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@dataclass
class SessionState:
    child_id: str
    skill_beliefs: Dict[str, SkillBelief]
    ability: float
    current_exercise: Optional[EXERCISE_SCHEMA]
    exercise_records: Dict[str, ExerciseRecord]
    attempt_log: List[Dict[str, Any]] = field(default_factory=list)
    session_xp: int = 0


def initialize_session(child_profile: Dict[str, Any]) -> SessionState:
    """
    Bootstraps the intelligence state for a new session.
    Reads BKT states, validates abilities, and pulls the first strategic exercise.
    """
    c_id = child_profile.get("child_id", "demo-id")
    raw_patterns = child_profile.get("error_patterns", {})
    beliefs = load_child_beliefs(raw_patterns)
    
    irt_ability = float(child_profile.get("irt_ability", 0.0))
    age = int(child_profile.get("age", 6))
    
    # Raw empty dict for records (should be loaded from DB, but keeping orchestration pure)
    records: Dict[str, ExerciseRecord] = {}

    # Pick starting exercise -> no review records yet, invoke TS selection
    first_skill = select_next_skill(beliefs)
    first_exercise = generate_exercise(first_skill, irt_ability, age)
    
    return SessionState(
        child_id=c_id,
        skill_beliefs=beliefs,
        ability=irt_ability,
        current_exercise=first_exercise,
        exercise_records=records,
        attempt_log=[],
        session_xp=0
    )


def process_response(
    state: SessionState, 
    answer: str, 
    response_time_ms: int
) -> Tuple[SessionState, Dict[str, Any]]:
    """
    The monolithic heartbeat of the adaptive logic loop.
    Absorbs an observation and mathematically alters BKT, IRT, and SM-2 matrices,
    followed by fetching the next optimal step.
    """
    if not state.current_exercise:
        # Should not occur in proper flow
        return state, {"error": "No active exercise"}

    # Extract exercise scope
    exercise = state.current_exercise
    target_skill = exercise["target_skill"]
    ex_id = exercise.get("id", f"{target_skill}_{int(datetime.now(timezone.utc).timestamp())}")
    
    # 1. Score answer
    expected = exercise["correct_answer"].strip().lower()
    actual = answer.strip().lower()
    is_correct = (expected == actual)
    
    # 2. Extract quality format for SM-2
    # Assume no explicit hints tracked yet in generic response object
    quality = compute_quality(is_correct, response_time_ms, False)
    
    # 3. Update Bayesian Matrix
    old_belief = state.skill_beliefs[target_skill]
    old_pk = old_belief.p_know
    new_belief = old_belief.update(is_correct)
    state.skill_beliefs[target_skill] = new_belief
    
    mastery_triggered = (new_belief.is_mastered and not old_belief.is_mastered)
    
    # 4. Update IRT (Learner Ability)
    item_diff = float(exercise["difficulty_rating"])
    old_ability = state.ability
    new_ability = estimate_ability_update(old_ability, item_diff, is_correct, response_time_ms)
    state.ability = new_ability
    
    # 5. Update SM-2 (Item Memory Tracker)
    if ex_id not in state.exercise_records:
        state.exercise_records[ex_id] = ExerciseRecord(ex_id, target_skill)
    record = state.exercise_records[ex_id]
    new_record = update_schedule(record, quality)
    state.exercise_records[ex_id] = new_record
    
    # 6. IRT (Item Calibration)
    # The new_calibrated difficulty (we omit saving it here as state.current_exercise is ending)
    calibrated_diff = calibrate_item_difficulty(item_diff, old_ability, is_correct)
    
    # 7. Progression - Decide what's Next
    # Review overdue SM-2 first
    prioritized_reviews = get_review_priority(list(state.exercise_records.values()))
    now = datetime.now(timezone.utc).timestamp()
    
    next_ex = None
    if prioritized_reviews and prioritized_reviews[0].next_review_date < now:
        # Inject old exercise for spaced repetition
        rec = prioritized_reviews[0]
        # In actual system, we'd pull the cached exercise from DB. 
        # Calling regenerate for mock purposes of orchestrator flow:
        next_ex = generate_exercise(rec.skill_id, state.ability, 6) 
    else:
        # Thompson sample new skill to drill
        next_skill = select_next_skill(state.skill_beliefs)
        next_ex = generate_exercise(next_skill, state.ability, 6)
        
    state.current_exercise = next_ex
    
    # 8. Compute Rewards
    xp_gain = 15 if is_correct else 5
    if mastery_triggered:
        xp_gain += 10
    state.session_xp += xp_gain
    
    # 9. Meta Logs
    state.attempt_log.append({
        "skill": target_skill,
        "correct": is_correct,
        "quality": quality,
        "time_ms": response_time_ms
    })
    
    # 10. Generate Feedback Context (Lightweight LLM)
    feedback_msg = _generate_feedback(is_correct, answer, expected)
    
    old_level = ability_to_level(old_ability)["level"]
    new_level_raw = ability_to_level(new_ability)["level"]
    
    resp_payload = {
        "is_correct": is_correct,
        "correct_answer": expected,
        "feedback_message": feedback_msg,
        "bkt_update": {
            "skill_id": target_skill, 
            "old_p_know": old_pk, 
            "new_p_know": new_belief.p_know, 
            "mastery_achieved": mastery_triggered
        },
        "irt_update": {
            "old_ability": old_ability, 
            "new_ability": new_ability, 
            "level_change": old_level != new_level_raw
        },
        "xp_earned": xp_gain,
        "next_exercise": next_ex,
        "session_stats": {
            "completed": len(state.attempt_log),
            "accuracy": sum(1 for a in state.attempt_log if a["correct"]) / len(state.attempt_log),
        }
    }
    
    return state, resp_payload


def _generate_feedback(is_correct: bool, answer: str, expected: str) -> str:
    """
    Calls a smaller, vastly faster model (llama-3.1-8b-instant) solely for 
    generating encouraging UI string responses. Minimizes latency compared to context LLMs.
    """
    if not GROQ_API_KEY:
        return "Great job!" if is_correct else "Keep trying, you've got this!"
        
    status = "right" if is_correct else "wrong"
    word_ref = expected if is_correct else answer
    
    prompt = f"Write ONE encouraging sentence for a 6-year-old who just got their spelling '{word_ref}' {status}. Max 8 words. Warm, not condescending. Tone: playful."
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 20
    }
    
    req = urllib.request.Request(GROQ_URL, data=json.dumps(payload).encode('utf-8'), 
                                 headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, 
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read())
            return data['choices'][0]['message']['content'].replace('"', '')
    except Exception:
        return "Excellent work!" if is_correct else "Nice try, keep going!"


def summarize_session(state: SessionState) -> Dict[str, Any]:
    """
    Compiles all delta events mathematically from start format to end format
    to pipeline back into the persistent DB state manager.
    """
    # Track regression and mastery maps
    mastered = []
    regressed = []
    bkt_deltas = {}
    
    # We lack DB load state here, so we track from internal objects
    for sid, belief in state.skill_beliefs.items():
        if belief.attempt_count > 0:
            end_p = belief.p_know
            bkt_deltas[sid] = {
                "end_p_know": end_p
            }
            if belief.is_mastered:
                mastered.append(sid)

    # Calculate worst state for next start
    focus = select_next_skill(state.skill_beliefs)
    
    avg_quality = 0.0
    if len(state.attempt_log) > 0:
        avg_quality = sum(a["quality"] for a in state.attempt_log) / len(state.attempt_log)
    
    return {
        "bkt_deltas": bkt_deltas,
        "ability_delta": state.ability, # We just return raw end
        "mastery_achieved": mastered,
        "skills_regressed": regressed, # Placeholder since old state delta tracking omitted initially
        "recommended_focus": focus,
        "session_quality_score": avg_quality / 5.0 # Normalized 0-1
    }
