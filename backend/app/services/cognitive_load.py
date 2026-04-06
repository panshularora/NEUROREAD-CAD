from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List

try:
    import textstat
except ImportError:
    textstat = None  # type: ignore
try:
    import spacy
except ImportError:
    spacy = None  # type: ignore


# Run once (when spacy is installed):
# python -m spacy download en_core_web_sm


# -------------------- NLP LOADER --------------------

@lru_cache(maxsize=1)
def get_nlp():
    """Lazy-load spaCy model once. Returns None if spacy not installed."""
    if spacy is None:
        return None
    return spacy.load("en_core_web_sm", exclude=["ner"])


# -------------------- DATA STRUCTURE --------------------

@dataclass
class CognitiveLoadResult:
    readability_score: float
    avg_sentence_length: float
    complex_word_ratio: float
    cognitive_load_score: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "readability_score": self.readability_score,
            "avg_sentence_length": self.avg_sentence_length,
            "complex_word_ratio": self.complex_word_ratio,
            "cognitive_load_score": self.cognitive_load_score,
        }


# -------------------- FEATURE EXTRACTORS --------------------

def compute_readability_score(text: str) -> float:
    if not text or text.isspace():
        return 100.0
    if textstat is None:
        return 50.0
    return float(textstat.flesch_reading_ease(text))


def compute_avg_sentence_length(text: str, doc=None) -> float:
    if not text or text.isspace():
        return 0.0

    if doc is None:
        nlp = get_nlp()
        if nlp is None:
            return float(len(text.split()))  # fallback: one sentence
        doc = nlp(text)

    sentence_lengths = []

    for sent in doc.sents:
        token_count = sum(1 for t in sent if t.is_alpha)
        if token_count > 0:
            sentence_lengths.append(token_count)

    if not sentence_lengths:
        return 0.0

    return sum(sentence_lengths) / len(sentence_lengths)


def compute_complex_word_ratio(text: str) -> float:
    if not text or text.isspace():
        return 0.0
    if textstat is None:
        return 0.2
    total_words = textstat.lexicon_count(text, removepunct=True)
    if total_words == 0:
        return 0.0

    complex_words = textstat.difficult_words(text)
    ratio = complex_words / total_words

    return max(0.0, min(1.0, float(ratio)))


# -------------------- SCORING LOGIC --------------------

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _map_to_cognitive_load(
    readability_score: float,
    avg_sentence_length: float,
    complex_word_ratio: float,
) -> float:

    fre_clamped = max(0.0, min(100.0, readability_score))
    readability_load = 1.0 - fre_clamped / 100.0
    readability_load = _clamp01(readability_load)

    sent_load = (avg_sentence_length - 5.0) / 30.0
    sent_load = _clamp01(sent_load)

    complex_load = complex_word_ratio / 0.30
    complex_load = _clamp01(complex_load)

    w_read, w_sent, w_complex = 0.4, 0.3, 0.3

    combined = (
        w_read * readability_load
        + w_sent * sent_load
        + w_complex * complex_load
    )

    return round(combined * 100.0, 2)


def get_difficulty_label(score: float) -> str:
    if score < 30:
        return "Low Cognitive Load"
    elif score < 60:
        return "Moderate Cognitive Load"
    else:
        return "High Cognitive Load"


# -------------------- DYSLEXIA SUPPORT UTILITIES --------------------

def extract_difficult_words_with_positions(text: str) -> List[Dict]:
    results = []
    if textstat is None:
        return results
    for match in re.finditer(r"\b\w+\b", text):
        word = match.group()
        clean = word.lower()

        if textstat.difficult_words(clean) > 0:
            results.append({
                "word": word,
                "start": match.start(),
                "end": match.end()
            })

    return results


def sentence_level_analysis(text: str, doc=None) -> List[Dict]:
    if doc is None:
        nlp = get_nlp()
        if nlp is None:
            return []
        doc = nlp(text)

    results = []

    for sent in doc.sents:
        sentence_text = sent.text.strip()
        if not sentence_text:
            continue

        readability = compute_readability_score(sentence_text)
        avg_len = compute_avg_sentence_length(sentence_text)
        complex_ratio = compute_complex_word_ratio(sentence_text)

        score = _map_to_cognitive_load(
            readability,
            avg_len,
            complex_ratio
        )

        results.append({
            "sentence": sentence_text,
            "score": score,
            "difficulty_label": get_difficulty_label(score)
        })

    return results


def estimate_reading_time(text: str) -> float:
    if textstat is None:
        return round(len((text or "").split()) / 200.0, 2)
    words = textstat.lexicon_count(text, removepunct=True)
    if words == 0:
        return 0.0

    minutes = words / 200
    return round(minutes, 2)


# -------------------- PUBLIC API --------------------

def calculate_cognitive_load(text: str) -> Dict:

    if not text or text.isspace():
        return {}

    nlp = get_nlp()
    if nlp is None:
        return {
            "readability_score": 50.0,
            "avg_sentence_length": 10.0,
            "complex_word_ratio": 0.2,
            "cognitive_load_score": 50.0,
            "difficulty_label": "Moderate Cognitive Load",
            "estimated_reading_time_minutes": estimate_reading_time(text),
            "difficult_words": [],
            "sentence_heatmap": [],
        }
    doc = nlp(text)

    readability = compute_readability_score(text)
    avg_len = compute_avg_sentence_length(text, doc)
    complex_ratio = compute_complex_word_ratio(text)
    final_score = _map_to_cognitive_load(readability, avg_len, complex_ratio)

    result = CognitiveLoadResult(
        readability_score=readability,
        avg_sentence_length=avg_len,
        complex_word_ratio=complex_ratio,
        cognitive_load_score=final_score,
    )

    return {
        **result.as_dict(),
        "difficulty_label": get_difficulty_label(final_score),
        "estimated_reading_time_minutes": estimate_reading_time(text),
        "difficult_words": extract_difficult_words_with_positions(text),
        "sentence_heatmap": sentence_level_analysis(text, doc)
    }


# -------------------- QUICK TEST --------------------

if __name__ == "__main__":
    sample = (
        "This is a simple sentence. "
        "However, the subsequent sentence, replete with specialized terminology "
        "and subordinate clauses, may impose a higher cognitive burden."
    )

    result = calculate_cognitive_load(sample)
    print(result)