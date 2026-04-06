from keybert import KeyBERT
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model():
    return KeyBERT()

def extract_keywords(text: str, top_n: int = 5):
    if not text or text.isspace():
        return []

    model = get_model()
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n
    )

    # Return only keyword strings
    return [kw[0] for kw in keywords]