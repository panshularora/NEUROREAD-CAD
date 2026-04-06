"""
Session Flow Engine

Converts disparate modules into a single contiguous river of adaptive learning.
Replaces menu-switching UI flows.

Algorithms cited:
- Zone of Proximal Development -> Vygotsky 1978 (used for computing Flow Score and optimal accuracy targeting)

Import Graph mapping structure for orchestrator reference:
learning_mode_api (wraps all) 
  --> session_flow
    --> multimodal_engine
    --> feedback_engine
    --> age_adapter
    --> exercise_taxonomy
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from app.services.learning.age_adapter import AgeProfile

@dataclass
class FlowState:
    phase: str
    exercises_in_phase: int
    phase_target: int
    flow_score: float
    boredom_signal: float
    anxiety_signal: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "exercises_in_phase": self.exercises_in_phase,
            "phase_target": self.phase_target,
            "flow_score": self.flow_score,
            "boredom_signal": self.boredom_signal,
            "anxiety_signal": self.anxiety_signal
        }

SESSION_PHASE_SEQUENCE = ["warmup", "core", "challenge", "cooldown", "celebration"]

def compute_flow_score(recent_attempts: List[Dict[str, Any]], age_profile: AgeProfile) -> Tuple[float, float, float]:
    """
    Computes Vygotsky's Zone of Proximal Development.
    Identifies if a child is bored, flowing, or anxious.
    """
    if len(recent_attempts) < 3:
        return (1.0, 0.0, 0.0) # Assume flowing initially
        
    recent_5 = recent_attempts[-5:]
    acc = sum(1 for a in recent_5 if a.get("correct", False)) / len(recent_5)
    
    times = [a.get("time_ms", 3000) for a in recent_5]
    time_increasing = False
    if len(times) >= 3:
        # Check if last two are slower than first two
        avg_early = sum(times[:2]) / 2.0
        avg_late = sum(times[-2:]) / 2.0
        if avg_late > avg_early + 500:
            time_increasing = True
            
    flow = 1.0
    boredom = 0.0
    anxiety = 0.0
    
    if acc < 0.70:
        flow = max(0.1, acc) # Drops with bad acc
        if time_increasing:
            anxiety = min(1.0, (0.70 - acc) * 2 + 0.3)
    elif acc > 0.85:
        flow = max(0.1, 1.0 - (acc - 0.85))
        if not time_increasing: # getting faster + easy
            boredom = min(1.0, (acc - 0.80) * 2 + 0.2)
            
    return (flow, boredom, anxiety)


def advance_phase(flow_state: FlowState, bkt_state: Dict[str, Any], age_profile: AgeProfile) -> FlowState:
    """Safely transitions between phases based on targets and emergency emotional signals."""
    f = FlowState(
        phase=flow_state.phase,
        exercises_in_phase=flow_state.exercises_in_phase + 1,
        phase_target=flow_state.phase_target,
        flow_score=flow_state.flow_score,
        boredom_signal=flow_state.boredom_signal,
        anxiety_signal=flow_state.anxiety_signal
    )
    
    # Emergency Anxiety Bailout
    if f.anxiety_signal > 0.8 and f.phase not in ["cooldown", "celebration"]:
        f.phase = "cooldown"
        f.exercises_in_phase = 0
        f.phase_target = 2
        return f
        
    # Emergency Boredom Hop
    if f.boredom_signal > 0.8 and f.phase == "warmup":
        f.phase = "core"
        f.exercises_in_phase = 0
        f.phase_target = int(age_profile.max_session_exercises * 0.6)
        return f
        
    # Standard phase check
    if f.exercises_in_phase >= f.phase_target:
        current_idx = SESSION_PHASE_SEQUENCE.index(f.phase)
        if current_idx < len(SESSION_PHASE_SEQUENCE) - 1:
            new_p = SESSION_PHASE_SEQUENCE[current_idx + 1]
            f.phase = new_p
            f.exercises_in_phase = 0
            
            # Reassign targets
            if new_p == "core":
                f.phase_target = int(age_profile.max_session_exercises * 0.6) # Variable middle
            elif new_p == "challenge":
                f.phase_target = 2
            elif new_p == "cooldown":
                f.phase_target = 2
            else:
                f.phase_target = 1 # celebration trigger
                
    return f

def get_next_exercise_in_flow(
    flow_state: FlowState,
    session_orchestrator_module: Any,
    session_state: Any,
    age_profile: AgeProfile
) -> Dict[str, Any]:
    """
    Hooks directly into the orchestrator logic to force phase-appropriate difficulty modifications.
    Note: Requires passing the orchestrator module reference to prevent circular imports.
    """
    if flow_state.phase == "celebration":
        return {} # Terminated
        
    # Store standard ability
    base_ability = getattr(session_state, "ability", 0.0)
    temp_ability = base_ability
    
    # Adjust for phase intent
    if flow_state.phase == "warmup":
        temp_ability = base_ability - 0.5
    elif flow_state.phase == "challenge":
        temp_ability = base_ability + 0.5
    elif flow_state.phase == "cooldown":
        temp_ability = base_ability - 0.3
        
    # Mutate state momentarily for the orchestrator to fetch
    if hasattr(session_state, "ability"):
        session_state.ability = temp_ability
        
    # In a real hook, we would call process_response here or allow the caller to.
    # Since we are returning the difficulty modification configuration, we just send it outward
    # alongside any forced high-confidence skill overrides.
    
    # Restore state immediately
    if hasattr(session_state, "ability"):
        session_state.ability = base_ability

    return {
        "overridden_ability_target": temp_ability,
        "is_challenge": flow_state.phase == "challenge",
        "is_cooldown": flow_state.phase == "cooldown"
    }
