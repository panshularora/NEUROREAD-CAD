"""
Content engine: serves words, phonics, and exercises tagged by difficulty.

Difficulty tiers:
- EASY (1): single letters, letter sounds, very short words
- MEDIUM (2): CVC words, simple words, short sentences
- HARD (3): longer words, sentences, comprehension
"""
from __future__ import annotations

import random
from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# Letter / phoneme content (EASY)
# ---------------------------------------------------------------------------
LETTERS = list("abcdefghijklmnopqrstuvwxyz")
# Commonly confused pairs for dyslexia (b/d, p/q, m/n, etc.)
CONFUSION_PAIRS = [
    ("b", "d"),
    ("p", "q"),
    ("m", "n"),
    ("u", "n"),
    ("f", "t"),
    ("g", "q"),
    ("s", "z"),
]

# ---------------------------------------------------------------------------
# Word banks by difficulty (MEDIUM = CVC/simple, HARD = longer)
# ---------------------------------------------------------------------------
WORDS_EASY: List[str] = [
    "cat", "dog", "run", "sit", "big", "red", "sun", "hat", "map", "pen",
    "bed", "leg", "top", "cup", "mug", "bug", "log", "hot", "not", "get",
]
WORDS_MEDIUM: List[str] = [
    "apple", "table", "water", "happy", "little", "letter", "number", "mother", "father", "sister",
    "flower", "butter", "rabbit", "pencil", "window", "garden", "yellow", "orange", "purple", "circle",
]
WORDS_HARD: List[str] = [
    "beautiful", "different", "important", "remember", "together", "because", "something", "everyone",
    "understand", "question", "exercise", "comprehension", "adventure", "mountain", "elephant",
]

# ---------------------------------------------------------------------------
# Sentences for guided reading / comprehension (by difficulty)
# ---------------------------------------------------------------------------
SENTENCES_EASY: List[str] = [
    "The cat sat.",
    "A dog ran.",
    "I see the sun.",
]
SENTENCES_MEDIUM: List[str] = [
    "The little dog ran in the garden.",
    "She has a red apple and a yellow pencil.",
    "We like to play in the water.",
]
SENTENCES_HARD: List[str] = [
    "The beautiful flower grew in the garden together with the others.",
    "It is important to remember that everyone is different.",
]


def get_letters_for_drill(confusion_focus: str | None = None, count: int = 5) -> List[Dict[str, Any]]:
    """Return letters for phonics drill. If confusion_focus e.g. 'b_d', include those letters."""
    if confusion_focus and "_" in confusion_focus:
        a, b = confusion_focus.split("_")[:2]
        pool = [a, b] + random.sample([c for c in LETTERS if c not in (a, b)], max(0, count - 2))
        random.shuffle(pool)
    else:
        pool = random.sample(LETTERS, min(count, len(LETTERS)))
    return [{"letter": c, "sound": _letter_sound(c)} for c in pool]


def _letter_sound(c: str) -> str:
    sounds = {
        "a": "/æ/", "b": "/b/", "c": "/k/", "d": "/d/", "e": "/ɛ/", "f": "/f/",
        "g": "/g/", "h": "/h/", "i": "/ɪ/", "j": "/dʒ/", "k": "/k/", "l": "/l/",
        "m": "/m/", "n": "/n/", "o": "/ɒ/", "p": "/p/", "q": "/kw/", "r": "/r/",
        "s": "/s/", "t": "/t/", "u": "/ʌ/", "v": "/v/", "w": "/w/", "x": "/ks/",
        "y": "/j/", "z": "/z/",
    }
    return sounds.get(c.lower(), "?")


def get_words_for_spelling(difficulty: int, count: int = 3, exclude: List[str] | None = None) -> List[str]:
    """Return words for spelling trainer by difficulty (1=easy, 2=medium, 3=hard)."""
    exclude = exclude or []
    if difficulty <= 1:
        pool = [w for w in WORDS_EASY if w not in exclude]
    elif difficulty == 2:
        pool = [w for w in WORDS_MEDIUM if w not in exclude]
    else:
        pool = [w for w in WORDS_HARD if w not in exclude]
    return random.sample(pool, min(count, len(pool))) if pool else []


def get_sentences_for_reading(difficulty: int, count: int = 1) -> List[str]:
    """Return sentences for guided reading by difficulty."""
    if difficulty <= 1:
        pool = SENTENCES_EASY
    elif difficulty == 2:
        pool = SENTENCES_MEDIUM
    else:
        pool = SENTENCES_HARD
    return random.sample(pool, min(count, len(pool)))


def get_comprehension_question_set(difficulty: int) -> List[Dict[str, Any]]:
    """Return MCQ-style comprehension questions (simplified; can be extended with real MCQs)."""
    # Placeholder: return question stubs. In production, tie to passages and options.
    base = [
        {"id": "q1", "question": "What is the main idea?", "options": ["A", "B", "C"], "correct": 0},
        {"id": "q2", "question": "What happened first?", "options": ["A", "B", "C"], "correct": 1},
    ]
    return base[: min(difficulty + 1, len(base))]
