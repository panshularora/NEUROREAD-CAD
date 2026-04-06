from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import Base, engine
from app.models.user import UserProfile
from app.models.child_learner import ChildLearner

app = FastAPI(title="NeuroAdapt AI Engine")

app.add_middleware(
    CORSMiddleware,
    # Vite dev server may be opened via localhost, 127.0.0.1, or LAN IP.
    # Use a regex so API calls don't fail due to Origin mismatch.
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|(\d{1,3}\.){3}\d{1,3})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static/audio folder exists
os.makedirs("static/audio", exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create DB tables + preload ML models
@app.on_event("startup")
def startup():
    # Database tables
    Base.metadata.create_all(bind=engine)

    # Preload semantic similarity model (sentence-transformers, singleton)
    try:
        from app.services.simplification_engine import load_semantic_model
        load_semantic_model()
    except Exception as exc:
        import logging
        logging.getLogger("startup").warning(
            "Semantic model preload failed (will lazy-load on first request): %s", exc
        )


@app.get("/")
def root():
    return {"message": "NeuroAdapt Backend Running"}


# Routes
from app.routes.simplify import router as simplify_router
app.include_router(simplify_router)

from app.routes.analyze import router as analyze_router
app.include_router(analyze_router)

from app.routes.vocab import router as vocab_router
app.include_router(vocab_router)

from app.routes.progress import router as progress_router
app.include_router(progress_router)

from app.routes.tts import router as tts_router
app.include_router(tts_router)

# New grouped routes (Assistive + Learning)
from app.routes.assistive.assist import router as assist_router
app.include_router(assist_router)

from app.routes.assistive.vocab import router as assistive_vocab_router
app.include_router(assistive_vocab_router)

from app.routes.assistive.tts import router as assistive_tts_router
app.include_router(assistive_tts_router)

from app.routes.assistive.simplify import router as assistive_simplify_router
app.include_router(assistive_simplify_router)

from app.routes.learning.phonics import router as learning_phonics_router
app.include_router(learning_phonics_router)

from app.routes.learning.exercises import router as learning_exercises_router
app.include_router(learning_exercises_router)

from app.routes.learning.spelling import router as learning_spelling_router
app.include_router(learning_spelling_router)

# Learning Mode: session, exercise, response, progress, recommendations
from app.routes.learning.session import router as learning_session_router
app.include_router(learning_session_router)

from app.routes.learning.flow_api import router as learning_flow_router
app.include_router(learning_flow_router)