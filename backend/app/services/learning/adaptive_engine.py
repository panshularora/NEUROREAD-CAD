"""
Adaptive learning engine for dyslexia-focused Learning Mode.

Logic:
1. Error pattern detection: when user confuses two letters (e.g. b/d), we increment
   a confusion counter for that pair. Above threshold → trigger focused exercises.
2. Difficulty scaling: EASY (letters) → MEDIUM (words) → HARD (sentences).
   Level is increased when success rate is high; decreased when low.
3. Reinforcement loop: weak areas (high error rate) are sampled more often;
   strong areas (low error rate) are sampled less often.
4. Smart recommendations: output human-readable focus areas and next steps.
"""
from __future__ import annotations

import json
from typing import Dict, List, Any, Tuple

# Confusion pairs we track (pattern_id -> (letter1, letter2))
CONFUSION_PATTERNS: Dict[str, Tuple[str, str]] = {
    "b_d_confusion": ("b", "d"),
    "p_q_confusion": ("p", "q"),
    "m_n_confusion": ("m", "n"),
    "u_n_confusion": ("u", "n"),
    "f_t_confusion": ("f", "t"),
}

# Threshold: if error rate for a pattern > this, we recommend focused practice
CONFUSION_THRESHOLD = 0.35

# Success rate thresholds for level change
SUCCESS_RATE_UP = 0.75   # Above this → consider level up
SUCCESS_RATE_DOWN = 0.45  # Below this → consider level down

# Minimum attempts before adjusting level
MIN_ATTEMPTS_FOR_LEVEL_CHANGE = 5


def parse_error_patterns(raw: str | None) -> Dict[str, float]:
    """Load error_patterns JSON from DB. Keys: pattern_id, values: error rate 0–1."""
    if not raw or not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def parse_progress_metrics(raw: str | None) -> Dict[str, float]:
    """Load progress_metrics JSON. Keys: module (phonics, spelling, etc.), values: 0–1 progress."""
    if not raw or not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def record_confusion_error(
    error_patterns: Dict[str, float],
    expected: str,
    actual: str,
    *,
    increment: float = 0.1,
    cap: float = 0.95,
) -> Dict[str, float]:
    """
    When user e.g. wrote 'd' instead of 'b', update b_d_confusion.
    expected/actual are single letters (lowercase).
    """
    updated = dict(error_patterns)
    for pattern_id, (a, b) in CONFUSION_PATTERNS.items():
        if (expected == a and actual == b) or (expected == b and actual == a):
            current = updated.get(pattern_id, 0.0)
            updated[pattern_id] = min(cap, current + increment)
            break
    return updated


def get_primary_confusion_focus(error_patterns: Dict[str, float]) -> str | None:
    """
    Return the pattern_id with highest error rate above CONFUSION_THRESHOLD.
    Used to drive content_engine to serve b/d or p/q focused drills.
    """
    above = [
        (pid, rate) for pid, rate in error_patterns.items()
        if rate >= CONFUSION_THRESHOLD
    ]
    if not above:
        return None
    above.sort(key=lambda x: -x[1])
    return above[0][0]


def compute_next_difficulty(
    current_level: int,
    recent_success_rate: float,
    recent_attempts: int,
) -> int:
    """
    Adaptive difficulty scaling:
    - If success rate high and enough attempts → level up (max 3).
    - If success rate low and enough attempts → level down (min 1).
    """
    if recent_attempts < MIN_ATTEMPTS_FOR_LEVEL_CHANGE:
        return current_level
    if recent_success_rate >= SUCCESS_RATE_UP and current_level < 3:
        return current_level + 1
    if recent_success_rate <= SUCCESS_RATE_DOWN and current_level > 1:
        return current_level - 1
    return current_level


def get_recommendations(
    error_patterns: Dict[str, float],
    progress_metrics: Dict[str, float],
    learning_level: int,
) -> List[Dict[str, Any]]:
    """
    Smart recommendation system: return list of focus areas and messages.
    Output format: [{ "id": "...", "type": "focus"|"tip", "message": "...", "priority": 1 }]
    """
    recs: List[Dict[str, Any]] = []

    # 1) Confusion-based: "Practice b/d distinction"
    focus = get_primary_confusion_focus(error_patterns)
    if focus:
        label = focus.replace("_confusion", "").replace("_", " vs ")
        recs.append({
            "id": f"focus_{focus}",
            "type": "focus",
            "message": f"Practice {label} distinction",
            "priority": 1,
        })

    # 2) Weakest module by progress (lowest progress_metrics value)
    if progress_metrics:
        sorted_mods = sorted(progress_metrics.items(), key=lambda x: x[1])
        weakest = sorted_mods[0]
        mod_name = weakest[0].replace("_", " ").title()
        recs.append({
            "id": f"module_{weakest[0]}",
            "type": "focus",
            "message": f"Spend more time on {mod_name}",
            "priority": 2,
        })

    # 3) Level-appropriate tip
    if learning_level <= 1:
        recs.append({
            "id": "tip_letters",
            "type": "tip",
            "message": "Focus on short vowel sounds",
            "priority": 3,
        })
    elif learning_level == 2:
        recs.append({
            "id": "tip_words",
            "type": "tip",
            "message": "Practice building simple words",
            "priority": 3,
        })
    else:
        recs.append({
            "id": "tip_sentences",
            "type": "tip",
            "message": "Try reading short sentences aloud",
            "priority": 3,
        })

    recs.sort(key=lambda x: x["priority"])
    return recs


def reinforcement_weights(
    error_patterns: Dict[str, float],
    module: str,
) -> float:
    """
    Return a weight for how often to show this module/pattern.
    Higher error rate → higher weight (repeat weak areas more often).
    """
    if module in ("phonics", "spelling") and error_patterns:
        # Average confusion rate as proxy for "need more practice"
        avg = sum(error_patterns.values()) / len(error_patterns) if error_patterns else 0
        return 0.5 + avg  # 0.5–1.45
    return 1.0
