"""
Spaced Repetition Engine (SM-2 + Forgetting Curve)

Applies SuperMemo-2 (SM-2) algorithms infused with Ebbinghaus memory curve mathematics.
Evaluates how well an answer was remembered, dictates interval scaling, 
and produces a retention decay score to trigger timely reviews.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

@dataclass
class ExerciseRecord:
    exercise_id: str
    skill_id: str
    easiness_factor: float = 2.5
    interval_days: int = 1
    repetitions: int = 0
    last_reviewed: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    next_review_date: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    history: List[Dict[str, Any]] = field(default_factory=list)

def compute_quality(is_correct: bool, response_time_ms: int, hint_used: bool) -> int:
    """
    Maps user interaction data into an SM-2 Quality score (0 to 5).
    
    0: No attempt / completely wrong
    1: Incorrect, but no hint / fast failure
    2: Incorrect, answered close
    3: Correct, but slow OR required a hint (struggled)
    4: Correct, normal speed, no hint
    5: Correct, fast response (< 2s), no hint (perfect recall)
    """
    if not is_correct:
        # Heuristics for incorrect
        if hint_used:
            return 1
        elif response_time_ms < 1000:
            # Too fast, probably careless completely
            return 0
        else:
            # Thought about it, got it wrong.
            return 2
            
    # From here, is_correct is True
    if hint_used:
        return 3
        
    if response_time_ms < 2000:
        return 5
    elif response_time_ms < 6000:
        return 4
    else:
        return 3
        
def update_schedule(record: ExerciseRecord, quality: int) -> ExerciseRecord:
    """
    Implements the core SM-2 algorithm to adjust easiness factors and calculate next interval.
    
    Math:
    EF_new = EF + (0.1 - (5-q)*(0.08 + (5-q)*0.02))
    New Factor minimum bounded to 1.3 to prevent exponential decay stalling.
    """
    now = datetime.now(timezone.utc).timestamp()
    
    # 1. Update EF based on SM-2 formula
    q = quality
    new_ef = record.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.3, new_ef)
    
    # 2. Update repetition and interval tier
    if q < 3:
        # Failed, reset streak to zero
        new_reps = 0
        new_interval = 1
    else:
        # Succeeded, increment streak
        new_reps = record.repetitions + 1
        if new_reps == 1:
            new_interval = 1
        elif new_reps == 2:
            new_interval = 6
        else:
            new_interval = max(1, round(record.interval_days * new_ef))
            
    # Ensure interval never goes above sensible limit for kids (e.g. 50 days max)
    new_interval = min(new_interval, 50)
    
    # 3. Apply dates
    next_date = now + (timedelta(days=new_interval).total_seconds())
    
    # Build updated instance
    history_copy = list(record.history)
    history_copy.append({
        "timestamp": now,
        "quality": q
    })
    
    return ExerciseRecord(
        exercise_id=record.exercise_id,
        skill_id=record.skill_id,
        easiness_factor=new_ef,
        interval_days=new_interval,
        repetitions=new_reps,
        last_reviewed=now,
        next_review_date=next_date,
        history=history_copy
    )

def retention_probability(record: ExerciseRecord) -> float:
    """
    Estimates the percentage chance the child remembers the item today, 
    using the Ebbinghaus forgetting curve simulation.
    
    Math: 
    R = exp(-t / S) where t = days since review, S = strength.
    Here strength is modeled via interval length * EF modifier.
    """
    now = datetime.now(timezone.utc).timestamp()
    days_since_review = (now - record.last_reviewed) / (60 * 60 * 24)
    
    if days_since_review <= 0:
        return 1.0
        
    # Calculate stability S
    # If rep is 0, stability is low. Else, it is the interval_days modified by EF
    if record.repetitions == 0:
        stability = 0.5 # Forget VERY fast
    else:
        stability = record.interval_days * (record.easiness_factor / 2.5)

    if stability <= 0:
        stability = 0.1
        
    prob = math.exp(-days_since_review / stability)
    return max(0.0, min(1.0, prob))

def get_review_priority(records: List[ExerciseRecord]) -> List[ExerciseRecord]:
    """
    Sorts exercise history by absolute urgency.
    Sorting Rules:
    1. Overdue Items (Date < Today)
    2. At-risk Items (Retention < 0.7)
    3. New items (Repetitions == 0)
    """
    now = datetime.now(timezone.utc).timestamp()
    
    def review_score(r: ExerciseRecord) -> float:
        # Generate sorting priority weighting (lower is closer to top of list)
        if r.next_review_date < now:
            # Overdue! Heavy priority (-100 minus days overdue limit)
            days_over = (now - r.next_review_date) / (60*60*24)
            return -100.0 - days_over
            
        ret_prob = retention_probability(r)
        if ret_prob < 0.70:
            # At risk! Prioritize by how close to zero retention it is
            return -50.0 + ret_prob
            
        if r.repetitions == 0:
            # Brand new, needs establishing
            return -10.0
            
        # Standard future item: prioritize by retention chance descending
        return ret_prob
        
    return sorted(records, key=review_score)
