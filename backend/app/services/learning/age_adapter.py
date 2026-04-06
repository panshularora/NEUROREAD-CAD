"""
Age Adapter Engine

Makes the system behave differently for early, developing, and fluent cohorts.
Adapts output bounds and enforces age-appropriate interactions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AgeProfile:
    age: int
    cohort: str
    max_session_exercises: int
    max_cognitive_load: int
    preferred_modalities: List[str]
    feedback_style: str
    word_length_limit: int
    distractor_count: int
    story_sentence_count: int
    tts_speed: float
    animation_intensity: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "age": self.age,
            "cohort": self.cohort,
            "max_session_exercises": self.max_session_exercises,
            "max_cognitive_load": self.max_cognitive_load,
            "preferred_modalities": self.preferred_modalities,
            "feedback_style": self.feedback_style,
            "word_length_limit": self.word_length_limit,
            "distractor_count": self.distractor_count,
            "story_sentence_count": self.story_sentence_count,
            "tts_speed": self.tts_speed,
            "animation_intensity": self.animation_intensity
        }


def get_age_profile(age: int) -> AgeProfile:
    """Generates the static bounds for the child's specific developmental stage."""
    if age < 7:
        return AgeProfile(
            age=age,
            cohort="early",
            max_session_exercises=6,
            max_cognitive_load=2,
            preferred_modalities=["audio", "motor"],
            feedback_style="celebratory",
            word_length_limit=3,
            distractor_count=2,
            story_sentence_count=1,
            tts_speed=0.7,
            animation_intensity="high"
        )
    elif age < 10:
        return AgeProfile(
            age=age,
            cohort="developing",
            max_session_exercises=10,
            max_cognitive_load=3,
            preferred_modalities=["visual", "audio"],
            feedback_style="encouraging",
            word_length_limit=5,
            distractor_count=3,
            story_sentence_count=2,
            tts_speed=0.85,
            animation_intensity="medium"
        )
    else:
        return AgeProfile(
            age=age,
            cohort="fluent",
            max_session_exercises=15,
            max_cognitive_load=5,
            preferred_modalities=["visual", "verbal"],
            feedback_style="informative",
            word_length_limit=8,
            distractor_count=4,
            story_sentence_count=4,
            tts_speed=1.0,
            animation_intensity="subtle"
        )


def adapt_exercise(exercise: Dict[str, Any], age_profile: AgeProfile, skill_beliefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes an LLM/Procedural generated exercise and trims it to perfectly match 
    the bounding rules of the AgeProfile.
    """
    adapted = dict(exercise)
    
    # 1. Trim Distractors
    if "distractors" in adapted:
        adapted["distractors"] = adapted["distractors"][:age_profile.distractor_count]
        
    # 2. Trim Story limits
    if "story_context" in adapted:
        sentences = [s.strip() for s in adapted["story_context"].replace('!', '.').replace('?', '.').split('.') if s.strip()]
        adapted["story_context"] = ". ".join(sentences[:age_profile.story_sentence_count]) + "."
        
    # 3. Replace long words using synonym map
    synonyms = {
        "peculiar": "weird",
        "strange": "odd",
        "enormous": "huge",
        "miniature": "tiny",
        "purchase": "buy",
        "beautiful": "pretty",
        "rapidly": "fast",
        "frequently": "often"
    }
    
    # Simple replace logic for correct_answer
    ans = adapted.get("correct_answer", "")
    if len(ans) > age_profile.word_length_limit:
        if ans.lower() in synonyms:
            adapted["correct_answer"] = synonyms[ans.lower()]
            
    # Apply global metadata
    adapted["tts_speed"] = age_profile.tts_speed
    adapted["animation_intensity"] = age_profile.animation_intensity
    adapted["feedback_style"] = age_profile.feedback_style
    adapted["age_cohort"] = age_profile.cohort
    
    return adapted


def estimate_fatigue(attempt_log: List[Dict[str, Any]], age_profile: AgeProfile) -> float:
    """
    Calculates cognitive exhaustion bounding from 0.0 to 1.0.
    Flags overloads to safely prompt a session conclusion.
    """
    if not attempt_log:
        return 0.0
        
    session_count = len(attempt_log)
    
    # 1. Time in session heuristic
    time_fatigue = (session_count / float(age_profile.max_session_exercises)) * 1.0
    
    # 2. Error rate in last 5
    recent = attempt_log[-5:]
    errors = sum(1 for a in recent if not a.get("correct", False))
    error_fatigue = errors * 0.08
    
    # 3. Response time trend
    time_trend_fatigue = 0.0
    if len(recent) >= 2:
        baseline = sum(a.get("time_ms", 3000) for a in recent[:-1]) / (len(recent) - 1)
        latest = recent[-1].get("time_ms", 3000)
        if latest > baseline:
            diff_ms = latest - baseline
            time_trend_fatigue = min(0.4, (diff_ms / 500.0) * 0.1)
            
    fatigue = time_fatigue + error_fatigue + time_trend_fatigue
    
    # 4. Recovery (correct + fast on last attempt)
    if recent and recent[-1].get("correct", False) and recent[-1].get("time_ms", 5000) < 2000:
        fatigue -= 0.05
        
    return max(0.0, min(1.0, fatigue))
