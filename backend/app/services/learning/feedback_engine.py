"""
Feedback Engine

Determines precisely what happens the moment a child interacts.
Shifts the app from a testing tool (Right/Wrong) to a teaching tool (Diagnostic/Remedial).
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

from app.services.learning.age_adapter import AgeProfile

# Simple edit distance manual implementation
def edit_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0: dp[i][j] = j
            elif j == 0: dp[i][j] = i
            elif s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1]
            else: dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
    return dp[m][n]

@dataclass
class FeedbackPlan:
    is_correct: bool
    feedback_type: str
    spoken_feedback: str
    visual_feedback: str
    error_analysis: Dict[str, Any]
    show_correct_answer: bool
    replay_stimulus: bool
    encouragement_level: str
    xp_animation: str
    next_hint_unlocked: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_correct": self.is_correct,
            "feedback_type": self.feedback_type,
            "spoken_feedback": self.spoken_feedback,
            "visual_feedback": self.visual_feedback,
            "error_analysis": self.error_analysis,
            "show_correct_answer": self.show_correct_answer,
            "replay_stimulus": self.replay_stimulus,
            "encouragement_level": self.encouragement_level,
            "xp_animation": self.xp_animation,
            "next_hint_unlocked": self.next_hint_unlocked
        }

FEEDBACK_TAXONOMY = {
    # Keys will be constructed dynamically in plan_feedback 
    # based on (is_correct, error_category, age_cohort)
    "CORRECT_FAST": "Lightning fast! Great job!",
    "CORRECT_NORMAL": "Exactly right!",
    "CORRECT_SLOW": "You worked it out, well done!",
    "MASTERY_ACHIEVED": "Incredible! You have mastered this sound!",
    "ERROR_PHONEME_SWAP_early": "Oops! Look closely—is that a b or a d?",
    "ERROR_PHONEME_SWAP_developing": "Watch out for those tricky letters. Let's look again.",
    "ERROR_PHONEME_SWAP_fluent": "Careful, that phoneme is easily swapped. Try to isolate the direction.",
    "ERROR_NEAR_MISS": "So close! One letter is off.",
    "ERROR_RANDOM": "Not quite. Let's listen together again.",
    "ERROR_TIMEOUT": "Take your time. Should we hear it again?",
}

def analyze_error(exercise: dict, child_answer: str, correct_answer: str, skill_id: str) -> Dict[str, Any]:
    """Diagnoses the exact nature of the child's failure."""
    
    ans = child_answer.lower()
    cor = correct_answer.lower()
    
    if not ans:
        return {"error_category": "ERROR_TIMEOUT", "confused_with": None}
        
    diffs = edit_distance(ans, cor)
    
    # 1. Phoneme Swap Detection
    target_pair = skill_id.split("_")[0] # 'bd', 'pq', 'mn'
    if diffs == 1 and len(ans) == len(cor):
        # Find the swapped char
        for a_char, c_char in zip(ans, cor):
            if a_char != c_char:
                if a_char in target_pair and c_char in target_pair:
                    return {
                        "error_category": "ERROR_PHONEME_SWAP",
                        "target_phoneme": c_char,
                        "confused_with": a_char,
                        "remediation_hint": "color_highlight"
                    }
    
    # 2. Near Miss
    if diffs <= 2:
        return {"error_category": "ERROR_NEAR_MISS", "confused_with": None}
        
    return {"error_category": "ERROR_RANDOM", "confused_with": None}


def generate_remediation_hint(error_analysis: Dict[str, Any], age_profile: AgeProfile, attempt_number: int) -> Dict[str, Any]:
    """Escalates help linearly based on struggle density."""
    if attempt_number == 1:
        return {"hint_type": "none", "encouragement": "normal"}
        
    if attempt_number == 2:
        target = error_analysis.get("target_phoneme", None)
        return {"hint_type": "color_highlight", "target_letter": target, "encouragement": "high"}
        
    if attempt_number == 3:
        target = error_analysis.get("target_phoneme", "")
        if target:
            return {"hint_type": "audio_phoneme", "phoneme": f"Remember, /{target}/ says '{target}uh'"}
        return {"hint_type": "replay_audio"}
        
    if attempt_number == 4:
        return {"hint_type": "reveal_answer", "explanation": "Let's see the right answer and move forward."}
        
    return {"hint_type": "escalate", "flag": True}


def plan_feedback(
    exercise: dict,
    child_answer: str,
    response_time_ms: int,
    attempt_number: int,
    consecutive_errors: int,
    age_profile: AgeProfile,
    bkt_update: dict,
    irt_update: dict
) -> FeedbackPlan:
    """Assembles all data streams into a cohesive next-2-seconds plan."""
    
    # 1. Base Truth
    is_correct = True
    ans = child_answer.lower()
    cor = exercise.get("correct_answer", "").lower()
    if ans != cor:
        is_correct = False
        
    skill_id = exercise.get("target_skill", "")
    err_data = {}
    f_type = "CORRECT_NORMAL"
    
    # 2. Mastery Override
    if bkt_update.get("mastery_achieved", False):
        f_type = "MASTERY_ACHIEVED"
        is_correct = True # Force success state if mastery pinged
        
    # 3. Categorization
    elif is_correct:
        if response_time_ms < 800 and attempt_number == 1:
            f_type = "CORRECT_FAST"
        elif response_time_ms > 6000:
            f_type = "CORRECT_SLOW"
    else:
        err_data = analyze_error(exercise, ans, cor, skill_id)
        raw_err = err_data["error_category"]
        if raw_err == "ERROR_PHONEME_SWAP":
            f_type = f"ERROR_PHONEME_SWAP_{age_profile.cohort}"
        else:
            f_type = raw_err
            
    # Lookup TTS
    spoken = FEEDBACK_TAXONOMY.get(f_type, "Let's keep going!")
    
    # Visual map
    visual = "star_burst"
    xp_anim = "+15 XP"
    replay = False
    show_corr = False
    
    if not is_correct:
        visual = "wobble"
        xp_anim = "none"
        if err_data.get("error_category") == "ERROR_RANDOM":
            replay = True
            
        if age_profile.age < 8 and attempt_number > 2:
            show_corr = True
            
    # Hint state & Encouragement
    enc_level = "normal"
    next_hint = False
    
    if consecutive_errors >= 5:
        enc_level = "high"
        
    rem_hint = generate_remediation_hint(err_data, age_profile, attempt_number)
    if rem_hint.get("hint_type") != "none":
        next_hint = True
        if rem_hint["hint_type"] == "reveal_answer":
            show_corr = True
            visual = "highlight_correct"
            
    if is_correct and rem_hint.get("hint_type") != "none":
        next_hint = False # Solved
        
    return FeedbackPlan(
        is_correct=is_correct,
        feedback_type=f_type,
        spoken_feedback=spoken,
        visual_feedback=visual,
        error_analysis=err_data,
        show_correct_answer=show_corr,
        replay_stimulus=replay,
        encouragement_level=enc_level,
        xp_animation=xp_anim,
        next_hint_unlocked=next_hint
    )
