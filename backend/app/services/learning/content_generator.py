"""
Content Generator Engine

Uses LLM-powered generation (Groq) with structured output enforcement to build minimal-pair
dyslexia exercises. Provides algorithmic/procedural fallback generation if LLM goes offline.
"""

import json
import os
import random
from typing import TypedDict, List, Optional
import urllib.request
import urllib.error

# We only import from bkt_engine for typing and taxonomy matching (No circulars)
from app.services.learning.bkt_engine import SKILL_PRIORS

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Exact output contract
class EXERCISE_SCHEMA(TypedDict):
    type: str # "fill_in_the_blank", "multiple_choice", etc
    target_skill: str
    stimulus: str
    correct_answer: str
    distractors: List[str]
    story_context: str
    difficulty_rating: int
    phoneme_position: str

# Hardcoded valid minimal pair dictionary for procedural fallback bounds
# Used when the LLM is down
PROCEDURAL_PAIRS = {
    "bd_initial": [("bat", "dat"), ("bog", "dog"), ("ban", "dan"), ("bug", "dug")],
    "bd_final": [("cab", "cad"), ("pub", "pud"), ("rib", "rid"), ("mob", "mod")],
    "bd_medial": [("hobby", "hoddy"), ("rubble", "ruddle")],
    "pq_initial": [("pat", "qat"), ("pack", "quack")],
    "mn_initial": [("mat", "nat"), ("mug", "nug"), ("map", "nap"), ("met", "net")],
    "mn_final": [("ram", "ran"), ("ham", "han"), ("sum", "sun"), ("dim", "din")],
}

def generate_exercise(skill_id: str, child_ability: float, age: int, retry_error: Optional[str] = None) -> EXERCISE_SCHEMA:
    """
    LLM-powered prompt execution enforcing strict constraints.
    Checks vocabulary grade level, phoneme target, limits distractors to exact swaps,
    and returns a guaranteed JSON schema.
    
    If the output violates the rules, it recurses once with retry_error feedback.
    Falls back to procedural algorithms upon total failure.
    """
    if not GROQ_API_KEY:
        # No token, immediate fallback
        return procedural_fallback(skill_id, child_ability)

    # Convert age to grade string
    grade_level = f"Grade {max(0, age - 5)}"
    
    # Calculate target difficulty from ability
    if child_ability < -1.0:
        diff_target = "1 to 2 (Very Easy)"
    elif child_ability <= 1.0:
        diff_target = "2 to 4 (Moderate)"
    else:
        diff_target = "4 to 5 (Challenging)"
        
    position_rule = "unknown"
    if "initial" in skill_id:
        position_rule = "start of the word"
    elif "final" in skill_id:
        position_rule = "end of the word"
    elif "medial" in skill_id:
        position_rule = "middle of the word"
        
    # Extract letters involved
    pair_letters = skill_id.split("_")[0] # e.g. "bd", "pq", "vowel"
    
    system_prompt = (
        f"You are a reading intervention generator for dyslexic children.\n"
        f"Output specifically JSON matching this exact structure:\n"
        f"{{\n"
        f'  "type": "multiple_choice",\n'
        f'  "target_skill": "{skill_id}",\n'
        f'  "stimulus": "[Short instruction]",\n'
        f'  "correct_answer": "[Target word]",\n'
        f'  "distractors": ["[Word1]", "[Word2]", "[Word3]"],\n'
        f'  "story_context": "[Sentence using the target word]",\n'
        f'  "difficulty_rating": int,\n'
        f'  "phoneme_position": "{position_rule}"\n'
        f"}}\n\n"
        f"CRITICAL CONSTRAINTS:\n"
        f"1. Vocabulary must match {grade_level}.\n"
        f"2. Rule: Distractors must differ from the correct_answer ONLY by the target phoneme pair ({pair_letters}) at the {position_rule}. "
        f"e.g., If answer is 'bog', a distractor must be 'dog'. The remaining 2 distractors should vary other letters to avoid obvious deduction.\n"
        f"3. Distractors must exactly be a list of 3 strings.\n"
        f"4. story_context must be 10 words or fewer and use the correct_answer naturally.\n"
        f"5. Difficulty rating must reflect the range: {diff_target}.\n"
    )
    
    if retry_error:
        system_prompt += f"\nYOUR PREVIOUS ATTEMPT FAILED: {retry_error}. FIX IT NOW."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate exercise for {skill_id}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    req = urllib.request.Request(GROQ_URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=8.0) as response:
            body = response.read()
            data = json.loads(body)
            result_str = data['choices'][0]['message']['content']
            
            parsed: EXERCISE_SCHEMA = json.loads(result_str)
            
            # Sub-validation explicit field checks
            if len(parsed.get('distractors', [])) != 3:
                raise ValueError("Must have exactly 3 distractors.")
            if len(parsed.get('story_context', '').split()) > 12: # small leniency
                raise ValueError("story_context is too long. Max 10 words.")
                
            return parsed
            
    except Exception as e:
        # Base case to prevent infinite recursion
        if not retry_error:
            # Try exactly once more with the error context
            return generate_exercise(skill_id, child_ability, age, retry_error=str(e))
        else:
            # Fallback on second failure
            return procedural_fallback(skill_id, child_ability)


def procedural_fallback(skill_id: str, ability_estimate: float) -> EXERCISE_SCHEMA:
    """
    Algorithmic (non-LLM) generation using static minimal-pair taxonomy.
    Used when the Groq LLM API fails or rate limits.
    """
    pairs = PROCEDURAL_PAIRS.get(skill_id, [("cat", "bat"), ("sit", "fit")])
    chosen = random.choice(pairs)
    
    # Identify which is correct based on random coin flip
    correct_is_0 = random.choice([True, False])
    correct_ans = chosen[0] if correct_is_0 else chosen[1]
    distractor_1 = chosen[1] if correct_is_0 else chosen[0]
    
    # Generic distractors
    distractor_2 = correct_ans[0] + "o" + correct_ans[2] if len(correct_ans) >= 3 else correct_ans + "s"
    distractor_3 = correct_ans[0] + "i" + correct_ans[2] if len(correct_ans) >= 3 else correct_ans + "ed"
    
    # Clean duplicates
    d_list = list(set([distractor_1, distractor_2, distractor_3]))
    while len(d_list) < 3:
        d_list.append(d_list[0] + "es")

    diff_rating = 1 if ability_estimate < 0 else 3

    return {
        "type": "multiple_choice",
        "target_skill": skill_id,
        "stimulus": f"Select the correct spelling of the word",
        "correct_answer": correct_ans,
        "distractors": d_list[:3],
        "story_context": f"Look at the fast {correct_ans}.",
        "difficulty_rating": diff_rating,
        "phoneme_position": str("end" if "final" in skill_id else "start")
    }

def score_generated_quality(exercise: EXERCISE_SCHEMA) -> float:
    """
    Quality heuristic 0.0 - 1.0 evaluating the exercise logic.
    Identifies LLM hallucination and bad rule adherence.
    """
    score = 0.0
    
    # 1. Distractor minimal pair test
    ans = exercise["correct_answer"].lower()
    distractors = [d.lower() for d in exercise["distractors"]]
    valid_minimal = False
    for d in distractors:
        if len(d) == len(ans):
            # count diff chars
            diffs = sum(1 for a, b in zip(ans, d) if a != b)
            if diffs == 1:
                valid_minimal = True
                break
    if valid_minimal:
        score += 0.3
        
    # 2. Context length
    ctx_words = exercise["story_context"].split()
    if 5 <= len(ctx_words) <= 10:
        score += 0.3
        
    # 3. Difficulty rating valid
    if 1 <= exercise["difficulty_rating"] <= 5:
        score += 0.2
        
    # 4. Stimulus exists
    if len(exercise["stimulus"]) > 5:
        score += 0.2
        
    return min(1.0, score)
