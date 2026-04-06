"""
Exercise Taxonomy Engine

Defines the complete library of exercise types, prerequisites, and dynamic
selection logic for dyslexic children. Replaces the 4 basic modules with
12 highly specific, multi-modal cognitive tasks.

Algorithms cited:
- Thompson Sampling -> Thompson 1933 (used for probabilistically balancing 
  exploration of new items vs exploitation of high-confusion items)
- BKT -> Corbett & Anderson 1994 (referenced via skill confusion)
- IRT -> Lord 1952 (referenced via irt_difficulty_range)
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any


class ExerciseType(Enum):
    PHONEME_ISOLATION = "PHONEME_ISOLATION"
    PHONEME_BLENDING = "PHONEME_BLENDING"
    PHONEME_SEGMENTATION = "PHONEME_SEGMENTATION"
    MINIMAL_PAIR_CHOICE = "MINIMAL_PAIR_CHOICE"
    LETTER_SOUND_MATCH = "LETTER_SOUND_MATCH"
    WORD_CONSTRUCTION = "WORD_CONSTRUCTION"
    RHYME_DETECTION = "RHYME_DETECTION"
    WORD_IN_CONTEXT = "WORD_IN_CONTEXT"
    STORY_COMPREHENSION = "STORY_COMPREHENSION"
    WORD_CHAIN = "WORD_CHAIN"
    SYLLABLE_CLAPPING = "SYLLABLE_CLAPPING"
    CONFUSABLE_SORT = "CONFUSABLE_SORT"


@dataclass
class ExerciseSpec:
    type: ExerciseType
    skill_ids: List[str]
    age_range: Tuple[int, int]
    modalities: List[str]
    cognitive_load: int
    prerequisite_types: List[ExerciseType]
    irt_difficulty_range: Tuple[float, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "skill_ids": self.skill_ids,
            "age_range": list(self.age_range),
            "modalities": self.modalities,
            "cognitive_load": self.cognitive_load,
            "prerequisite_types": [pt.value for pt in self.prerequisite_types],
            "irt_difficulty_range": list(self.irt_difficulty_range),
        }


# The directed graph of what must be attempted/mastered before unlocking
EXERCISE_PREREQUISITES: Dict[ExerciseType, List[ExerciseType]] = {
    ExerciseType.PHONEME_ISOLATION: [],
    ExerciseType.LETTER_SOUND_MATCH: [],
    ExerciseType.SYLLABLE_CLAPPING: [],
    ExerciseType.RHYME_DETECTION: [ExerciseType.PHONEME_ISOLATION],
    ExerciseType.PHONEME_BLENDING: [ExerciseType.PHONEME_ISOLATION],
    ExerciseType.PHONEME_SEGMENTATION: [ExerciseType.PHONEME_BLENDING],
    ExerciseType.MINIMAL_PAIR_CHOICE: [ExerciseType.LETTER_SOUND_MATCH],
    ExerciseType.CONFUSABLE_SORT: [ExerciseType.MINIMAL_PAIR_CHOICE],
    ExerciseType.WORD_CONSTRUCTION: [ExerciseType.PHONEME_BLENDING, ExerciseType.LETTER_SOUND_MATCH],
    ExerciseType.WORD_CHAIN: [ExerciseType.WORD_CONSTRUCTION],
    ExerciseType.WORD_IN_CONTEXT: [ExerciseType.WORD_CONSTRUCTION],
    ExerciseType.STORY_COMPREHENSION: [ExerciseType.WORD_IN_CONTEXT],
}

# The library of all specs
# Broad skill groups map to the BKT models.
ALL_SPECS = [
    ExerciseSpec(ExerciseType.PHONEME_ISOLATION, ["bd_initial", "pq_initial", "mn_initial", "vowel_ae"], (4, 12), ["audio", "visual"], 1, EXERCISE_PREREQUISITES[ExerciseType.PHONEME_ISOLATION], (-4.0, 0.0)),
    ExerciseSpec(ExerciseType.LETTER_SOUND_MATCH, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (4, 12), ["visual", "audio", "motor"], 1, EXERCISE_PREREQUISITES[ExerciseType.LETTER_SOUND_MATCH], (-4.0, -1.0)),
    ExerciseSpec(ExerciseType.SYLLABLE_CLAPPING, ["vowel_ae", "vowel_eo", "vowel_ui"], (4, 9), ["audio", "motor"], 2, EXERCISE_PREREQUISITES[ExerciseType.SYLLABLE_CLAPPING], (-3.0, 1.0)),
    ExerciseSpec(ExerciseType.RHYME_DETECTION, ["vowel_ae", "vowel_eo", "vowel_ui", "bd_final", "mn_final", "pq_final"], (4, 10), ["audio", "visual"], 2, EXERCISE_PREREQUISITES[ExerciseType.RHYME_DETECTION], (-2.5, 1.0)),
    ExerciseSpec(ExerciseType.PHONEME_BLENDING, ["bd_initial", "pq_initial", "mn_initial", "bd_medial", "vowel_ae", "vowel_eo", "vowel_ui"], (5, 12), ["audio", "verbal"], 3, EXERCISE_PREREQUISITES[ExerciseType.PHONEME_BLENDING], (-2.0, 2.0)),
    ExerciseSpec(ExerciseType.PHONEME_SEGMENTATION, ["bd_initial", "pq_initial", "mn_initial", "bd_final", "pq_final", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (5, 12), ["audio", "motor"], 3, EXERCISE_PREREQUISITES[ExerciseType.PHONEME_SEGMENTATION], (-1.5, 2.5)),
    ExerciseSpec(ExerciseType.MINIMAL_PAIR_CHOICE, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final"], (5, 12), ["audio", "visual"], 2, EXERCISE_PREREQUISITES[ExerciseType.MINIMAL_PAIR_CHOICE], (-2.0, 3.0)),
    ExerciseSpec(ExerciseType.CONFUSABLE_SORT, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final"], (5, 12), ["visual", "motor"], 3, EXERCISE_PREREQUISITES[ExerciseType.CONFUSABLE_SORT], (-1.0, 2.0)),
    ExerciseSpec(ExerciseType.WORD_CONSTRUCTION, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (6, 12), ["visual", "motor", "audio"], 4, EXERCISE_PREREQUISITES[ExerciseType.WORD_CONSTRUCTION], (0.0, 4.0)),
    ExerciseSpec(ExerciseType.WORD_CHAIN, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (7, 12), ["visual", "motor"], 4, EXERCISE_PREREQUISITES[ExerciseType.WORD_CHAIN], (0.5, 4.0)),
    ExerciseSpec(ExerciseType.WORD_IN_CONTEXT, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (6, 12), ["visual", "audio"], 4, EXERCISE_PREREQUISITES[ExerciseType.WORD_IN_CONTEXT], (1.0, 4.0)),
    ExerciseSpec(ExerciseType.STORY_COMPREHENSION, ["bd_initial", "bd_medial", "bd_final", "pq_initial", "pq_final", "mn_initial", "mn_final", "vowel_ae", "vowel_eo", "vowel_ui"], (7, 12), ["audio", "visual", "verbal"], 5, EXERCISE_PREREQUISITES[ExerciseType.STORY_COMPREHENSION], (2.0, 4.0)),
]

def select_exercise_type(
    child_ability: float,
    child_age: int,
    skill_beliefs: Dict[str, Any],
    recent_type_history: List[ExerciseType],
    session_fatigue_score: float
) -> ExerciseType:
    """
    Selects the optimal ExerciseType based on a strict criteria waterfall.
    Uses Thompson Sampling inspired weighted logic for the final candidates.
    """
    # 1 & 2: Age and Ability valid
    candidates = []
    for spec in ALL_SPECS:
        if spec.age_range[0] <= child_age <= spec.age_range[1]:
            if spec.irt_difficulty_range[0] <= child_ability <= spec.irt_difficulty_range[1]:
                candidates.append(spec)

    # 3: Prerequisites met (p_know > 0.4 on skills associated with those types)
    # For simplicity of graph parsing in this function, we assume if the prerequisites
    # exist, the child must have some mastery (>0.4 p_know) of the skills tied to the prerequisites.
    valid_candidates = []
    for spec in candidates:
        prereqs_met = True
        for prereq_type in spec.prerequisite_types:
            # find the spec for this prereq
            prereq_spec = next((s for s in ALL_SPECS if s.type == prereq_type), None)
            if prereq_spec:
                # check if mean p_know of prereq skills > 0.4
                p_knows = [skill_beliefs.get(s, getattr(skill_beliefs.get(s, None), 'p_know', 0.0)) for s in prereq_spec.skill_ids]
                # Extract actual float values if they are SkillBelief objects mapping
                p_knows_floats = []
                for pk in p_knows:
                    if hasattr(pk, 'p_know'):
                        p_knows_floats.append(pk.p_know)
                    elif isinstance(pk, (float, int)):
                        p_knows_floats.append(float(pk))
                    else:
                        p_knows_floats.append(0.0)
                
                if p_knows_floats:
                    mean_p_know = sum(p_knows_floats) / len(p_knows_floats)
                    if mean_p_know <= 0.4:
                        prereqs_met = False
                        break
        if prereqs_met:
            valid_candidates.append(spec)

    if not valid_candidates:
        # Fallback to isolation if all else fails
        return ExerciseType.PHONEME_ISOLATION

    # 5: Cognitive Load Gating
    if session_fatigue_score > 0.7:
        low_load = [s for s in valid_candidates if s.cognitive_load <= 2]
        if low_load:
            valid_candidates = low_load

    weights = []
    for spec in valid_candidates:
        # Calculate mean confusion priority
        confusions = []
        for s in spec.skill_ids:
            belief = skill_beliefs.get(s)
            if hasattr(belief, 'confusion_priority'):
                confusions.append(belief.confusion_priority)
            elif hasattr(belief, 'p_know'):
                confusions.append(1.0 - belief.p_know)
            else:
                confusions.append(1.0)
                
        mean_confusion = sum(confusions) / max(1, len(confusions))

        # Weight base calculation
        weight = mean_confusion * (1.0 / max(1, spec.cognitive_load))

        # 4: Fatigue avoidance (penalty for repetition)
        recent_count = sum(1 for rt in recent_type_history if rt == spec.type)
        if recent_count >= 3:
            weight *= 0.2

        # 6: Modality rotation
        last_primary = ""
        if recent_type_history:
            last_type = recent_type_history[-1]
            last_spec = next((s for s in ALL_SPECS if s.type == last_type), None)
            if last_spec and last_spec.modalities:
                last_primary = last_spec.modalities[0]
        
        if spec.modalities and last_primary and spec.modalities[0] != last_primary:
            weight *= 1.5 # Boost weight if it shifts the perceptual channel

        weights.append(weight)

    # 7: Thompson-Sampling inspired selection
    # We add a small randomness factor by sampling using the calculated weight as a shape modifier
    sampled_weights = [random.betavariate(w + 1.0, 2.0) for w in weights]
    best_idx = sampled_weights.index(max(sampled_weights))
    
    return valid_candidates[best_idx].type
