"""
NeuroRead Text Simplification Engine V2
========================================

Production-grade pipeline for dyslexic readability:

  Layer 0 — Preprocessing  : Clean, normalize, truncate
  Layer 1 — LLM Primary    : Groq API (dynamic, level-aware prompt)
  Layer 2 — Post-Processing : Sentence splitting & shortening
  Layer 3 — Validation      : Semantic similarity + readability + cognitive load
  Layer 4 — Fallback        : Qwen/HF API (last resort)

Author: NeuroRead Team
Version: v2
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import logging
import os
import re
import threading
import time
import uuid
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

# ────────────────────────────── LOGGING ──────────────────────────────

logger = logging.getLogger("simplification_engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(_handler)

# ────────────────────────────── CONFIG ───────────────────────────────

PIPELINE_VERSION = "v2"

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Validation thresholds
SEMANTIC_SIM_THRESHOLD = float(os.getenv("SEMANTIC_SIM_THRESHOLD", "0.90"))

# Cache
CACHE_MAX_SIZE = 256
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

# Input limits
MAX_INPUT_LENGTH = 2000

# Reading mode targets (words per sentence)
LEVEL_CONFIG = {
    "easy": 8,
    "moderate": 12,
    "light": 15,
}

# ────────────────────────────── ERROR CLASSES ────────────────────────


class SimplificationError(Exception):
    """Base error for simplification pipeline."""
    pass


class SimplificationTimeoutError(SimplificationError):
    """LLM call exceeded timeout."""
    pass


class SimplificationAPIError(SimplificationError):
    """LLM API returned an error."""
    pass


class SimplificationValidationError(SimplificationError):
    """Output failed semantic/readability validation."""
    pass


# ────────────────────────── SEMANTIC SIMILARITY ────────────────────

_semantic_model = None


def load_semantic_model():
    """Load sentence-transformer model at startup (singleton)."""
    global _semantic_model
    if _semantic_model is not None:
        logger.info("Semantic model already loaded, skipping.")
        return

    logger.info("Loading semantic similarity model: all-MiniLM-L6-v2 ...")
    start = time.time()

    try:
        from sentence_transformers import SentenceTransformer
        _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
        elapsed = round(time.time() - start, 2)
        logger.info("Semantic model loaded in %.2fs", elapsed)
    except Exception as exc:
        logger.error("Failed to load semantic model: %s", exc)
        _semantic_model = None


def semantic_similarity(original: str, simplified: str) -> float:
    """Compute cosine similarity between original and simplified text."""
    if _semantic_model is None:
        logger.warning("Semantic model not loaded — skipping similarity check.")
        return 1.0  # assume pass if model unavailable

    try:
        from sentence_transformers import util
        emb1 = _semantic_model.encode(original, convert_to_tensor=True)
        emb2 = _semantic_model.encode(simplified, convert_to_tensor=True)
        score = util.cos_sim(emb1, emb2)
        return float(score)
    except Exception as exc:
        logger.error("Semantic similarity computation failed: %s", exc)
        return 1.0  # fail open


# ────────────────────── TIMEOUT & RETRY HELPERS ─────────────────────

def with_timeout(func, *args, timeout: float = 2.0):
    """Run func with a timeout. Raises SimplificationTimeoutError on expiry."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise SimplificationTimeoutError(
                f"{func.__name__} exceeded {timeout}s timeout"
            )


def retry(func, *args, retries: int = 2, timeout: float = 2.0):
    """Retry func with timeout. Returns None if all attempts fail."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return with_timeout(func, *args, timeout=timeout)
        except (SimplificationTimeoutError, SimplificationAPIError) as exc:
            last_exc = exc
            logger.warning("Attempt %d/%d failed: %s", attempt, retries, exc)
        except Exception as exc:
            last_exc = exc
            logger.error("Attempt %d/%d unexpected error: %s", attempt, retries, exc)
            break  # don't retry non-transient errors
    logger.error("All %d retries exhausted. Last error: %s", retries, last_exc)
    return None


# ─────────────────── LAYER 0: PREPROCESSING ─────────────────────────

def preprocess(text: str) -> str:
    """Clean, normalize, and truncate input text."""
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]
        logger.warning("Input truncated to %d characters.", MAX_INPUT_LENGTH)
    return text


# ─────────────────── LAYER 1: LLM SIMPLIFICATION ───────────────────

DYSLEXIA_SYSTEM_PROMPT = """You are an expert reading assistant for people with dyslexia.

Rewrite the text using:
- Short sentences (max {target_len} words per sentence)
- Format the output with clear line breaks between each sentence (e.g. Sentence 1.\n\nSentence 2.)
- If the input is long (multiple paragraphs), break it into smaller paragraphs, ensuring each paragraph contains only 2–3 short sentences
- Preserve the original structure but simplify progressively across the entire text
- Do not truncate or omit any part of the content
- Simple words (common vocabulary)
- Clear structure (one idea per sentence)
- No complex clauses
- Natural English (do NOT sound robotic)

Additional Rules:
- Do NOT repeat the same idea.
- Avoid vague phrases (e.g. do not say "it is a big deal").
- Keep explanations meaningful, not childish.
- Do not simplify proper nouns or key technical terms (e.g., names, Formula One, FIA).
- Ensure sentences connect logically and do not feel disconnected.

Keep the meaning EXACTLY the same."""


def _llm_simplify(text: str, level: str = "easy") -> str:
    """Primary simplification via Groq LLM with dynamic prompt."""
    target_len = LEVEL_CONFIG.get(level, 12)
    system_prompt = DYSLEXIA_SYSTEM_PROMPT.format(target_len=target_len)

    if not GROQ_API_KEY:
        raise SimplificationAPIError("No GROQ_API_KEY configured.")

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text:\n{text}"},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        result = response.choices[0].message.content.strip()
        if not result:
            raise SimplificationAPIError("Groq returned empty response.")
        return result

    except SimplificationAPIError:
        raise
    except Exception as exc:
        raise SimplificationAPIError(f"Groq API call failed: {exc}") from exc


# We need a wrapper that captures level for retry()
def _make_llm_call(text: str, level: str) -> str:
    """Wrapper for _llm_simplify to work with retry()."""
    return _llm_simplify(text, level)


# ─────────────────── LAYER 2: POST-PROCESSING ──────────────────────

def split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex."""
    return [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]


def split_into_shorter(sentence: str, max_words: int = 12) -> list[str]:
    """Break a long sentence into chunks of max_words."""
    words = sentence.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        # Add period to chunks that don't end with punctuation
        if chunk and chunk[-1] not in ".!?":
            chunk += "."
        chunks.append(chunk)
    return chunks


def remove_redundancy(sentences: list[str]) -> list[str]:
    """Remove exact duplicate sentences (case-insensitive) to reduce repetition."""
    seen = set()
    result = []
    for s in sentences:
        key = s.lower().strip()
        if key not in seen:
            seen.add(key)
            result.append(s)
    return result


def post_process(text: str, max_words: int = 15) -> str:
    """Split any remaining long sentences after LLM simplification."""
    sentences = split_sentences(text)
    result = []

    for s in sentences:
        if len(s.split()) > max_words:
            result.extend(split_into_shorter(s, max_words))
        else:
            result.append(s)

    result = remove_redundancy(result)
    return "\n\n".join(result)


# ─────────────────── LAYER 3: VALIDATION ────────────────────────────

def validate_output(original: str, simplified: str, level: str) -> Dict[str, Any]:
    """
    Run 3 validators:
      1. Semantic similarity (>= threshold)
      2. Avg sentence length (<= target for level)
      3. Cognitive load (real score, skip if unavailable)

    Returns:
        {
            "passed": bool,
            "reason": str,
            "metrics": {
                "semantic_similarity": float,
                "avg_sentence_length": float,
                "cognitive_load_before": float,
                "cognitive_load_after": float,
                "readability_score_before": float,
                "readability_score_after": float,
            }
        }
    """
    result: Dict[str, Any] = {"passed": True, "reason": "", "metrics": {}}

    # Sanity check
    if len(simplified.strip()) < 10:
        return {"passed": False, "reason": "Output too short or empty", "metrics": {}}

    # ── Validator 1: Semantic similarity ──
    sim_score = semantic_similarity(original, simplified)
    result["metrics"]["semantic_similarity"] = round(sim_score, 3)

    if sim_score < SEMANTIC_SIM_THRESHOLD:
        result["passed"] = False
        result["reason"] = (
            f"Semantic similarity too low: {sim_score:.3f} < {SEMANTIC_SIM_THRESHOLD}"
        )
        return result

    # ── Validator 2: Readability — avg sentence length ──
    sentences = split_sentences(simplified)
    total_words = sum(len(s.split()) for s in sentences)
    avg_len = total_words / max(len(sentences), 1)
    result["metrics"]["avg_sentence_length"] = round(avg_len, 1)

    target_len = LEVEL_CONFIG.get(level, 12)
    if avg_len > target_len + 3:
        logger.warning(
            "Avg sentence length %.1f exceeds target %d (+3 tolerance)",
            avg_len, target_len
        )

    # ── Validator 3: Cognitive load (real, skip if unavailable) ──
    try:
        from app.services.cognitive_load import calculate_cognitive_load
        orig_analysis = calculate_cognitive_load(original)
        simp_analysis = calculate_cognitive_load(simplified)
        result["metrics"]["cognitive_load_before"] = orig_analysis.get(
            "cognitive_load_score", 0.0
        )
        result["metrics"]["cognitive_load_after"] = simp_analysis.get(
            "cognitive_load_score", 0.0
        )
        result["metrics"]["readability_score_before"] = orig_analysis.get(
            "readability_score", 0.0
        )
        result["metrics"]["readability_score_after"] = simp_analysis.get(
            "readability_score", 0.0
        )
    except Exception:
        logger.info("Cognitive load service unavailable — skipping metric.")
        result["metrics"]["cognitive_load_before"] = 0.0
        result["metrics"]["cognitive_load_after"] = 0.0
        result["metrics"]["readability_score_before"] = 0.0
        result["metrics"]["readability_score_after"] = 0.0

    return result


# ─────────────────── LAYER 4: FALLBACK ──────────────────────────────

def _fallback_qwen(text: str, level: str = "easy") -> Optional[str]:
    """
    Last-resort fallback using the existing Qwen/HF Inference API.
    Re-uses the existing simplifier service.
    """
    try:
        from app.services.assistive.simplifier import simplify_text as qwen_simplify

        # Map level string to int for Qwen service
        level_map = {"easy": 1, "moderate": 2, "light": 3}
        int_level = level_map.get(level, 1)

        logger.info("Triggering Qwen (HF) fallback...")
        result = qwen_simplify(text, int_level)

        if isinstance(result, dict):
            return result.get("simplified_text", "")
        return str(result)

    except Exception as exc:
        logger.error("Qwen fallback failed: %s", exc)
        return None


# ─────────────────── THREAD-SAFE CACHE ──────────────────────────────

_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()


def _cache_key(text: str, level: str) -> str:
    """Stable, deterministic cache key including pipeline version."""
    raw = f"{text.strip()}::{level}::{PIPELINE_VERSION}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    """Thread-safe cache lookup with TTL check."""
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        if time.time() - entry.get("_ts", 0) > CACHE_TTL_SECONDS:
            del _cache[key]
            return None
        # Return a copy without internal timestamp
        result = {k: v for k, v in entry.items() if k != "_ts"}
        return result


def _cache_set(key: str, value: Dict[str, Any]):
    """Thread-safe cache store with LRU eviction."""
    with _cache_lock:
        if len(_cache) >= CACHE_MAX_SIZE:
            # Evict oldest entries (by timestamp)
            sorted_keys = sorted(
                _cache, key=lambda k: _cache[k].get("_ts", 0)
            )
            for k in sorted_keys[:len(sorted_keys) // 2]:
                del _cache[k]
        store = value.copy()
        store["_ts"] = time.time()
        _cache[key] = store


# ─────────────────── MAIN PIPELINE ──────────────────────────────────

def process_text(text: str, level: str = "easy") -> Dict[str, Any]:
    """
    Main V2 simplification pipeline.

    Flow:
        0. Preprocess input
        1. Cache lookup → return if hit
        2. Primary LLM simplification (Groq, 2s timeout, 2 retries)
        3. Post-process (split long sentences)
        4. Validate (semantic similarity + readability + cognitive load)
        5. If failed → Qwen/HF fallback (2s timeout, 2 retries)
        6. Cache result and return

    Returns:
        {
            "simplified_text": str,
            "cognitive_load_before": float,
            "cognitive_load_after": float,
            "used_fallback": bool,
            "fallback_source": str | None,
            "avg_sentence_length": float,
            "semantic_similarity": float,
            "readability_score_before": float,
            "readability_score_after": float,
            "pipeline_time_ms": float,
            "pipeline_version": str,
        }
    """
    request_id = uuid.uuid4().hex[:8]
    start = time.time()

    # ── Layer 0: Preprocess ──
    text = preprocess(text)

    if not text:
        return {
            "simplified_text": "",
            "cognitive_load_before": 0.0,
            "cognitive_load_after": 0.0,
            "used_fallback": False,
            "fallback_source": None,
            "avg_sentence_length": 0.0,
            "semantic_similarity": 0.0,
            "readability_score_before": 0.0,
            "readability_score_after": 0.0,
            "pipeline_time_ms": 0.0,
            "pipeline_version": PIPELINE_VERSION,
        }

    # ── Step 1: Cache lookup ──
    key = _cache_key(text, level)
    cached = _cache_get(key)
    if cached is not None:
        logger.info("[%s] Cache HIT for key=%s", request_id, key)
        cached["pipeline_time_ms"] = 0.0
        return cached

    logger.info(
        "[%s] Processing text (%d chars) through V2 pipeline | level=%s",
        request_id, len(text), level,
    )

    used_fallback = False
    fallback_source = None
    simplified = None

    # ── Step 2: Primary LLM (Groq) ──
    logger.info("[%s] Layer 1: Running Groq LLM simplification...", request_id)
    simplified = retry(_make_llm_call, text, level, retries=2, timeout=5.0)

    if simplified:
        # ── Step 3: Post-process ──
        target_words = LEVEL_CONFIG.get(level, 12)
        logger.info("[%s] Layer 2: Post-processing (max %d words/sentence)...", request_id, target_words)
        simplified = post_process(simplified, max_words=target_words + 5)

        # ── Step 4: Validate ──
        logger.info("[%s] Layer 3: Running validation...", request_id)
        validation = validate_output(text, simplified, level)

        if validation["passed"]:
            logger.info("[%s] Validation PASSED.", request_id)
        else:
            logger.warning(
                "[%s] Validation FAILED: %s — triggering fallback.",
                request_id, validation["reason"],
            )
            simplified = None  # force fallback
    else:
        logger.warning("[%s] Primary LLM returned no result — triggering fallback.", request_id)
        validation = {"passed": False, "reason": "Primary LLM failed", "metrics": {}}

    # ── Step 5: Fallback (if needed) ──
    if simplified is None:
        logger.info("[%s] Layer 4: Trying Qwen (HF) fallback...", request_id)
        qwen_result = retry(_fallback_qwen, text, level, retries=2, timeout=5.0)

        if qwen_result and len(qwen_result.strip()) > 10:
            target_words = LEVEL_CONFIG.get(level, 12)
            simplified = post_process(qwen_result, max_words=target_words + 5)
            used_fallback = True
            fallback_source = "qwen"

            # Re-validate fallback output
            validation = validate_output(text, simplified, level)
            if validation["passed"]:
                logger.info("[%s] Qwen fallback PASSED validation.", request_id)
            else:
                logger.warning(
                    "[%s] Qwen fallback also failed validation: %s — using best effort.",
                    request_id, validation["reason"],
                )
        else:
            # All fallbacks failed — return preprocessed original as last resort
            logger.error("[%s] ALL fallbacks failed — returning original text.", request_id)
            simplified = text
            used_fallback = True
            fallback_source = "best_effort"
            validation = validate_output(text, simplified, level)

    # ── Build response ──
    elapsed_ms = round((time.time() - start) * 1000, 1)
    metrics = validation.get("metrics", {})
    
    avg_len = metrics.get("avg_sentence_length", 0.0)
    sim_score = metrics.get("semantic_similarity", 0.0)
    target_words = LEVEL_CONFIG.get(level, 12)
    confidence = (0.6 * sim_score) + (0.4 * max(0.0, 1.0 - (avg_len / target_words)))

    result = {
        "simplified_text": simplified,
        "cognitive_load_before": metrics.get("cognitive_load_before", 0.0),
        "cognitive_load_after": metrics.get("cognitive_load_after", 0.0),
        "used_fallback": used_fallback,
        "fallback_source": fallback_source,
        "avg_sentence_length": avg_len,
        "semantic_similarity": sim_score,
        "readability_score_before": metrics.get("readability_score_before", 0.0),
        "readability_score_after": metrics.get("readability_score_after", 0.0),
        "confidence_score": round(confidence, 3),
        "pipeline_time_ms": elapsed_ms,
        "pipeline_version": PIPELINE_VERSION,
    }

    # ── Step 6: Cache result ──
    _cache_set(key, result)

    # ── Structured logging ──
    logger.info(
        "[SIMPLIFY] request_id=%s | latency=%dms | similarity=%.2f | "
        "avg_sent_len=%.1f | fallback=%s | version=%s",
        request_id, elapsed_ms,
        result["semantic_similarity"],
        result["avg_sentence_length"],
        fallback_source or "none",
        PIPELINE_VERSION,
    )

    return result