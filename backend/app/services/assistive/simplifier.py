import os
import json
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

# Hugging Face Inference API (e.g. Qwen)
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
HF_MODEL = os.getenv("HF_SIMPLIFIER_MODEL", "Qwen/Qwen2.5-7B-Instruct")

def _fallback_simplify(text: str, level: int) -> Dict[str, Any]:
    """Deterministic local fallback when the LLM call fails."""
    import re

    t = " ".join((text or "").strip().split())
    if not t:
        return {
            "simplified_text": "",
            "bullet_points": [],
            "definitions": {},
            "step_by_step_explanation": [],
        }

    # More aggressive simplification at lower levels.
    max_sentences = 3 if level == 1 else 5 if level == 2 else 8
    max_len = 120 if level == 1 else 160 if level == 2 else 220

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
    short = []
    for s in sentences[:max_sentences]:
        if len(s) > max_len:
            s = s[: max_len - 1].rstrip() + "…"
        short.append(s)

    simplified_text = " ".join(short)
    bullet_points = short

    return {
        "simplified_text": simplified_text,
        "bullet_points": bullet_points,
        "definitions": {},
        "step_by_step_explanation": bullet_points,
    }


def simplify_text(text: str, level: int) -> Dict[str, Any]:
    """Call Hugging Face Inference API (e.g. Qwen) to simplify text for neurodiverse learners."""
    system_prompt = """
You are an AI accessibility assistant for neurodiverse learners.

Simplify the given text based on the level:

Level 1 = very simple, short sentences.
Level 2 = moderately simplified.
Level 3 = lightly simplified.

Return ONLY valid JSON in this exact format:

{
  "simplified_text": "...",
  "bullet_points": ["..."],
  "definitions": {"term": "..."},
  "step_by_step_explanation": ["step 1", "step 2"]
}

Do not return anything outside JSON.
"""

    user_prompt = f"""
Simplification level: {level}

Text:
{text}
"""

    # Single prompt for HF Inference API (no chat endpoint needed)
    full_prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"

    if not HF_TOKEN:
        return _fallback_simplify(text, level)

    url = f"{HF_API_BASE}/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.3,
            "return_full_text": False,
            "do_sample": True,
        },
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # HF returns list of dicts with "generated_text" when return_full_text=False
        if isinstance(data, list) and data and isinstance(data[0], dict):
            content = (data[0].get("generated_text") or "").strip()
        elif isinstance(data, dict) and "generated_text" in data:
            content = (data.get("generated_text") or "").strip()
        else:
            content = ""
    except Exception:
        # If the provider is unreachable (network/DNS/timeout), fall back so the API doesn't 500.
        return _fallback_simplify(text, level)

    try:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {
            "simplified_text": content,
            "bullet_points": [],
            "definitions": {},
            "step_by_step_explanation": [],
        }