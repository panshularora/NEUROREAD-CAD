from fastapi import APIRouter
from pydantic import BaseModel
from app.services.user_profile import update_user_profile
from app.services.accessibility import (
    apply_dyslexia_formatting,
    generate_audio_payload
)
from app.services.assistive.keyword_extractor import extract_keywords
from app.services.assistive.tts_service import generate_speech_audio

# ── Hybrid simplification engine (primary path) ──
from app.services.simplification_engine import process_text

# Optional: spacy/textstat for cognitive load (requires C++ build tools on Windows)
try:
    from app.services.cognitive_load import calculate_cognitive_load
    _cognitive_load_available = True
except Exception:
    _cognitive_load_available = False
    def calculate_cognitive_load(text: str):
        return {"cognitive_load_score": 50.0, "readability_score": 50.0}

router = APIRouter()


class SimplifyRequest(BaseModel):
    text: str
    level: int | None = None
    user_id: str | None = None
    profile: str | None = "default"
    enable_dyslexia_support: bool = True
    enable_audio: bool = True


def _int_level_to_str(level: int) -> str:
    """Convert numeric level (1-3) to engine string level."""
    if level == 1:
        return "easy"
    elif level == 2:
        return "moderate"
    else:
        return "light"


@router.post("/simplify")

def simplify(request: SimplifyRequest):

    # 1️⃣ Analyze original (or use defaults if cognitive_load not available)
    original_analysis = calculate_cognitive_load(request.text)
    original_score = original_analysis["cognitive_load_score"]

    # 2️⃣ Auto level
    if request.level is None:
        if original_score < 30:
            level = 3
        elif original_score < 60:
            level = 2
        else:
            level = 1
    else:
        level = request.level

    # Profile override
    if request.profile == "focus":
        level = 1
    elif request.profile == "easy_read":
        level = 1
    elif request.profile == "academic":
        level = 3

    # 3️⃣ Run hybrid simplification pipeline (FLAN-T5 → Constraints → QC → Fallbacks)
    engine_level = _int_level_to_str(level)
    engine_result = process_text(request.text, level=engine_level)

    simplified_text = engine_result["simplified_text"]
    used_fallback = engine_result["used_fallback"]
    fallback_source = engine_result.get("fallback_source")

    # Use engine's cognitive load scores
    cognitive_load_before = engine_result["cognitive_load_before"]
    cognitive_load_after = engine_result["cognitive_load_after"]

    # 4️⃣ Re-analyze simplified for the full analysis dict
    simplified_analysis = calculate_cognitive_load(simplified_text)
    simplified_score = simplified_analysis["cognitive_load_score"]

    reduction = original_score - simplified_score

    # 5️⃣ Overload detection
    overload_warning = None
    isolation_mode = False

    if original_score >= 70:
        overload_warning = "This text may cause cognitive overload."
        isolation_mode = True

    # 6️⃣ Dyslexia Formatting
    dyslexia_view = None
    if request.enable_dyslexia_support:
        dyslexia_view = apply_dyslexia_formatting(simplified_text)

    # 7️⃣ Adaptive Audio Mode
    audio_payload = None
    if request.enable_audio:
        audio_payload = generate_audio_payload(simplified_text)

    # 8️⃣ Save progress
    if request.user_id:
        update_user_profile(
            user_id=request.user_id,
            level=level,
            score=simplified_score
        )

    impact_percentage = 0
    if original_score > 0:
        impact_percentage = round((reduction / original_score) * 100, 1)

    # Generate TTS automatically for simplified text (best-effort)
    audio_url = None
    try:
        tts_result = generate_speech_audio(simplified_text, slow=False)
        audio_url = tts_result.audio_url
    except Exception:
        audio_url = None

    # Keywords for convenience (used by new assistive endpoints too)
    keywords = extract_keywords(request.text)

    return {
        "auto_selected_level": level,
        "profile_used": request.profile,
        "overload_warning": overload_warning,
        "isolation_mode": isolation_mode,
        "original_analysis": original_analysis,
        "simplified_text": simplified_text,
        "dyslexia_optimized_text": dyslexia_view,
        "audio_mode": audio_payload,
        "simplified_analysis": simplified_analysis,
        "cognitive_load_reduction": round(reduction, 2),
        "impact_summary": f"Cognitive load reduced by {round(reduction, 2)} points ({impact_percentage}% improvement)",
        "audio_file": audio_url,
        "keywords": keywords,
        # ── V2 engine metrics ──
        "cognitive_load_before": cognitive_load_before,
        "cognitive_load_after": cognitive_load_after,
        "used_fallback": used_fallback,
        "fallback_source": fallback_source,
        "avg_sentence_length": engine_result.get("avg_sentence_length", 0.0),
        "semantic_similarity": engine_result.get("semantic_similarity", 0.0),
        "readability_score_before": engine_result.get("readability_score_before", 0.0),
        "readability_score_after": engine_result.get("readability_score_after", 0.0),
        "confidence_score": engine_result.get("confidence_score", 0.0),
        "pipeline_version": engine_result.get("pipeline_version", "v2"),
        "pipeline_time_ms": engine_result["pipeline_time_ms"],
    }


# New path (keeps legacy `/simplify` working too)
@router.post("/assistive/simplify")
def simplify_assistive(request: SimplifyRequest):
    return simplify(request)
