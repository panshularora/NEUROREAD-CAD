from __future__ import annotations

import re
from typing import Dict, List


def generate_comprehension_questions(text: str, *, max_questions: int = 3) -> Dict[str, object]:
    """Generate simple comprehension questions.

    Heuristic approach: ask about key nouns/subjects and overall meaning.
    """
    if not text or text.isspace():
        return {"questions": []}

    cleaned = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]

    questions: List[str] = []
    if sentences:
        questions.append("What is the main idea of the text in one sentence?")
        questions.append(f"What happens in the first part: \"{sentences[0]}\"?")
        if len(sentences) > 1:
            questions.append(f"What happens next after: \"{sentences[0]}\"?")

    return {"questions": questions[: max(1, max_questions)]}

