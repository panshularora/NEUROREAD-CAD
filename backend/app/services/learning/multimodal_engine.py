"""
Multimodal Engine

The perceptual layer defining how data is presented visually, auditorily, and motorically.
Ensures we leverage dyslexia-friendly non-text channels effectively.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from app.services.learning.exercise_taxonomy import ExerciseType
from app.services.learning.age_adapter import AgeProfile

# Research-backed color pairs creating extreme visual discordance to prevent inversion confusion
PHONEME_COLORS = {
    "b": "blue",
    "d": "orange",
    "p": "purple",
    "q": "green",
    "m": "teal",
    "n": "coral",
    "target_default": "gold",
    "neutral": "charcoal"
}

@dataclass
class LetterTile:
    letter: str
    color: str
    size_px: int
    is_target: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "letter": self.letter,
            "color": self.color,
            "size_px": self.size_px,
            "is_target": self.is_target
        }

@dataclass
class ModalityPlan:
    primary_modality: str
    stimulus_format: str
    response_format: str
    tts_text: str
    tts_speed: float
    highlight_pattern: str
    letter_color_map: Dict[str, str]
    animation_cue: str
    tile_layout: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "primary_modality": self.primary_modality,
            "stimulus_format": self.stimulus_format,
            "response_format": self.response_format,
            "tts_text": self.tts_text,
            "tts_speed": self.tts_speed,
            "highlight_pattern": self.highlight_pattern,
            "letter_color_map": self.letter_color_map,
            "animation_cue": self.animation_cue
        }
        if self.tile_layout is not None:
            d["tile_layout"] = self.tile_layout
        return d


def generate_tts_instruction(exercise_type: ExerciseType, exercise: dict, age_profile: AgeProfile) -> str:
    """
    36 Exact TTS Instruction Templates bounded by cohort.
    Ensures instructions never exceed working memory limits of the specific age band.
    """
    cohort = age_profile.cohort
    target = exercise.get("target_skill", "").split("_")[0] 
    target_name = target if target else "this"
    word = exercise.get("correct_answer", "the word")
    
    templates = {
        ExerciseType.PHONEME_ISOLATION: {
            "early": f"What is the first sound in {word}?",
            "developing": f"Listen to the word {word}. Which sound comes first?",
            "fluent": f"Identify the initial phoneme in the word {word}."
        },
        ExerciseType.PHONEME_BLENDING: {
            "early": "Listen to the sounds. Blend the word.",
            "developing": "Listen to these letter sounds. What word do they make?",
            "fluent": "Blend the following phonemes into a complete word."
        },
        ExerciseType.PHONEME_SEGMENTATION: {
            "early": f"Tap out the sounds in {word}.",
            "developing": f"Listen to {word}. Tap the screen for each distinct sound.",
            "fluent": f"Segment the word {word} into its individual phonemes."
        },
        ExerciseType.MINIMAL_PAIR_CHOICE: {
            "early": f"Which word is {word}?",
            "developing": f"Listen carefully. Which of these words is {word}?",
            "fluent": f"Select the correct spelling for the spoken word: {word}."
        },
        ExerciseType.LETTER_SOUND_MATCH: {
            "early": f"Which sound does this letter make?",
            "developing": f"Look at the letter on screen. Which sound matches?",
            "fluent": f"Identify the correct phoneme associated with the displayed grapheme."
        },
        ExerciseType.WORD_CONSTRUCTION: {
            "early": f"Spell the word {word}.",
            "developing": f"Drag the letters to correctly spell the word {word}.",
            "fluent": f"Assemble the letter tiles to form the target word: {word}."
        },
        ExerciseType.RHYME_DETECTION: {
            "early": "Do these words rhyme?",
            "developing": "Listen to both words. Do they have a rhyming sound?",
            "fluent": "Determine if the following pair of words constitute a rhyme."
        },
        ExerciseType.WORD_IN_CONTEXT: {
            "early": "Which word finishes the sentence?",
            "developing": "Read the sentence and choose the word that fits best.",
            "fluent": "Select the appropriate vocabulary word to complete the context."
        },
        ExerciseType.STORY_COMPREHENSION: {
            "early": "Listen to the story. Answer the question.",
            "developing": "Listen closely to this short story, then answer the question.",
            "fluent": "Comprehend the following narrative passage and address the question."
        },
        ExerciseType.WORD_CHAIN: {
            "early": "Change one letter to make the new word.",
            "developing": "Change a single letter to build the next word in the chain.",
            "fluent": "Substitute one grapheme to construct the subsequent linked word."
        },
        ExerciseType.SYLLABLE_CLAPPING: {
            "early": f"How many claps in {word}?",
            "developing": f"Listen to {word}. Tap the drum for every syllable you hear.",
            "fluent": f"Determine the total syllable count for the word {word}."
        },
        ExerciseType.CONFUSABLE_SORT: {
            "early": f"Sort the words with {target_name}.",
            "developing": f"Sort these words into the right buckets based on their letters.",
            "fluent": f"Categorize the following terms according to their target graphemes."
        }
    }
    
    # Fallback safety if exercise mapping misses
    if exercise_type not in templates:
        return f"Solve this {exercise_type.value} exercise."
        
    return templates[exercise_type].get(cohort, templates[exercise_type]["fluent"])


def plan_modality(
    exercise_type: ExerciseType,
    exercise: dict,
    age_profile: AgeProfile,
    recent_modalities: List[str],
    child_ability: float
) -> ModalityPlan:
    """
    Takes an exercise framework and overlays the sensory presentation rules.
    """
    
    # 1. Modality Rotation and Priorities
    primary = "visual"
    # Force audio if early age constraint, OR if visual was overused
    if age_profile.age < 7:
        primary = "audio"
    elif len(recent_modalities) >= 2 and recent_modalities[-1] == "visual" and recent_modalities[-2] == "visual":
        primary = "audio"
        
    stimulus = "text+audio" if age_profile.age < 7 else "text"
    
    # 2. Response Formats
    r_format = "select"
    if exercise_type in [ExerciseType.WORD_CONSTRUCTION, ExerciseType.CONFUSABLE_SORT]:
        r_format = "drag"
    elif exercise_type in [ExerciseType.PHONEME_SEGMENTATION, ExerciseType.SYLLABLE_CLAPPING]:
        r_format = "tap"
    elif age_profile.age < 7:
        r_format = "tap" if r_format == "select" else r_format
    elif age_profile.age >= 10 and exercise_type == ExerciseType.WORD_CONSTRUCTION:
        r_format = "type"
        
    # 3. Highlight Patterns
    highlight = "word"
    if exercise_type in [ExerciseType.PHONEME_ISOLATION, ExerciseType.PHONEME_BLENDING]:
        highlight = "phoneme"
    elif exercise_type == ExerciseType.SYLLABLE_CLAPPING:
        highlight = "syllable"
        
    # 4. Global Dyslexic Color Map Overlay
    # Always send so the UI can retro-paint text instantly
    color_map = dict(PHONEME_COLORS)
    
    # Generate instructions
    tts = generate_tts_instruction(exercise_type, exercise, age_profile)
    
    # 8. Tile Layouts for Construction
    tiles = None
    if exercise_type in [ExerciseType.WORD_CONSTRUCTION, ExerciseType.CONFUSABLE_SORT]:
        ans = exercise.get("correct_answer", "")
        # Mix letters of correct answer + some distractors
        letters = list(set(list(ans) + ["b", "d", "p"])) # inject known confusables as bait
        random.shuffle(letters)
        
        size = 80 if age_profile.age < 7 else (60 if age_profile.age < 10 else 40)
        tiles = []
        for l in letters:
            col = color_map.get(l, color_map["neutral"])
            # In sort, everything might be a target, in construction, only letters in word are relevant targets
            is_tgt = l in ans
            tiles.append(LetterTile(letter=l, color=col, size_px=size, is_target=is_tgt).to_dict())

    return ModalityPlan(
        primary_modality=primary,
        stimulus_format=stimulus,
        response_format=r_format,
        tts_text=tts,
        tts_speed=age_profile.tts_speed,
        highlight_pattern=highlight,
        letter_color_map=color_map,
        animation_cue="pulse",
        tile_layout=tiles
    )
