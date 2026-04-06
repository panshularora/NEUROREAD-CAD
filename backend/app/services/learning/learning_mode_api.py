"""
Learning Mode API Interface

The single unified Python entrypoint for the entire adaptive learning subsystem.
Connects the discrete ML modules into a consumable flow for endpoints.
"""

from typing import Dict, Any, List

from app.services.learning import session_orchestrator as orch
from app.services.learning import exercise_taxonomy as tax
from app.services.learning import age_adapter as age
from app.services.learning import multimodal_engine as multi
from app.services.learning import feedback_engine as fb
from app.services.learning import session_flow as flow

class LearningModeAPI:
    def __init__(self, groq_client: Any = None, db_session_factory: Any = None):
        """
        Initializes logic controllers. Does not instantiate database state until usage.
        """
        self.groq = groq_client
        self.db = db_session_factory
        
        # Simulated memory persistence for standard continuous running during testing
        self._active_sessions: Dict[str, Any] = {}
        self._active_flows: Dict[str, flow.FlowState] = {}
        self._active_profiles: Dict[str, age.AgeProfile] = {}
        self._modality_history: Dict[str, List[str]] = {}
        self._exercise_history: Dict[str, List[tax.ExerciseType]] = {}
        self._consecutive_errors: Dict[str, int] = {}
        
    def start_session(self, child_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Boots a fresh continuous ZPD river."""
        
        # 1. Age Profiles
        raw_age = child_profile.get("age", 6)
        profile = age.get_age_profile(raw_age)
        
        # 2. Base ML State
        ml_state = orch.initialize_session(child_profile)
        sess_id = ml_state.child_id + "_sys"
        
        # 3. Flow Tracking
        f_state = flow.FlowState(phase="warmup", exercises_in_phase=0, phase_target=2, flow_score=1.0, boredom_signal=0.0, anxiety_signal=0.0)
        
        self._active_sessions[sess_id] = ml_state
        self._active_flows[sess_id] = f_state
        self._active_profiles[sess_id] = profile
        self._modality_history[sess_id] = []
        self._exercise_history[sess_id] = []
        self._consecutive_errors[sess_id] = 0
        
        # 4. Generate first Exercise Structure using Taxonomy
        raw_ex_dict = ml_state.current_exercise if ml_state.current_exercise else {}
        if not raw_ex_dict:
            raw_ex_dict = {"target_skill": "bd_initial", "correct_answer": "bat", "distractors": ["dat", "pat"]}
            
        ex_type = tax.select_exercise_type(ml_state.ability, raw_age, ml_state.skill_beliefs, [], 0.0)
        self._exercise_history[sess_id].append(ex_type)
        
        # 5. Multimodal Overlay
        mod_plan = multi.plan_modality(ex_type, raw_ex_dict, profile, [], ml_state.ability)
        self._modality_history[sess_id].append(mod_plan.primary_modality)
        
        # 6. Assemble
        fully_adapted = age.adapt_exercise(raw_ex_dict, profile, ml_state.skill_beliefs)
        fully_adapted["modality_plan"] = mod_plan.to_dict()
        fully_adapted["exercise_type"] = ex_type.value
        
        return {
            "session_id": sess_id,
            "age_profile": profile.to_dict(),
            "flow_state": f_state.to_dict(),
            "first_exercise": fully_adapted,
            "session_config": {
                "max_exercises": profile.max_session_exercises,
                "tts_speed": profile.tts_speed,
                "animation_intensity": profile.animation_intensity,
                "letter_colors": multi.PHONEME_COLORS
            }
        }
        
    def submit_answer(self, session_id: str, answer: str, response_time_ms: int) -> Dict[str, Any]:
        """Injects performance data, loops orchestration, and produces tailored feedback & next steps."""
        
        ml_state = self._active_sessions.get(session_id)
        f_state = self._active_flows.get(session_id)
        profile = self._active_profiles.get(session_id)
        
        if not ml_state or not f_state or not profile:
            raise ValueError("Invalid session pointer")
            
        current_ex = ml_state.current_exercise
        
        # Track attempts and errors
        prev_attempts = len(ml_state.attempt_log)
        
        # 1. Orchestrator Processing
        new_state, resp_dict = orch.process_response(ml_state, answer, response_time_ms)
        self._active_sessions[session_id] = new_state
        
        # Extract specifics
        is_correct = resp_dict["is_correct"]
        if not is_correct:
            self._consecutive_errors[session_id] += 1
        else:
            self._consecutive_errors[session_id] = 0
            
        # 2. Determine Feedback Plan
        fb_plan = fb.plan_feedback(
            exercise=current_ex if current_ex else {},
            child_answer=answer,
            response_time_ms=response_time_ms,
            attempt_number=self._consecutive_errors[session_id] + 1,
            consecutive_errors=self._consecutive_errors[session_id],
            age_profile=profile,
            bkt_update=resp_dict["bkt_update"],
            irt_update=resp_dict["irt_update"]
        )
        
        # 3. Flow and Phase Calculation
        flo, bo, anx = flow.compute_flow_score(new_state.attempt_log, profile)
        f_state.flow_score = flo
        f_state.boredom_signal = bo
        f_state.anxiety_signal = anx
        
        f_state = flow.advance_phase(f_state, new_state.skill_beliefs, profile)
        self._active_flows[session_id] = f_state
        
        # 4. Fatigue Score Check
        fatigue = age.estimate_fatigue(new_state.attempt_log, profile)
        sess_end = False
        end_reason = None
        if fatigue >= 0.85:
            sess_end = True
            end_reason = "fatigue"
        elif len(new_state.attempt_log) >= profile.max_session_exercises:
            sess_end = True
            end_reason = "max_reached"
        elif f_state.phase == "celebration":
            sess_end = True
            end_reason = "all_mastered"
            
        next_ex_payload = None
        if not sess_end:
            # 5. Build Next Exercise
            next_raw = new_state.current_exercise
            ex_type = tax.select_exercise_type(new_state.ability, profile.age, new_state.skill_beliefs, self._exercise_history[session_id], fatigue)
            self._exercise_history[session_id].append(ex_type)
            
            mod_plan = multi.plan_modality(ex_type, next_raw if next_raw else {}, profile, self._modality_history[session_id], new_state.ability)
            self._modality_history[session_id].append(mod_plan.primary_modality)
            
            next_ex_payload = age.adapt_exercise(next_raw if next_raw else {}, profile, new_state.skill_beliefs)
            next_ex_payload["modality_plan"] = mod_plan.to_dict()
            next_ex_payload["exercise_type"] = ex_type.value

        return {
            "feedback": fb_plan.to_dict(),
            "bkt_update": resp_dict["bkt_update"],
            "irt_update": resp_dict["irt_update"],
            "flow_state": f_state.to_dict(),
            "fatigue_score": fatigue,
            "session_should_end": sess_end,
            "end_reason": end_reason,
            "next_exercise": next_ex_payload,
            "session_stats": resp_dict["session_stats"]
        }
        
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """Provides the aggregate JSON wrap for DB persistence."""
        ml_state = self._active_sessions.get(session_id)
        if not ml_state:
            return {"error": "Invalid session"}
            
        return orch.summarize_session(ml_state)
