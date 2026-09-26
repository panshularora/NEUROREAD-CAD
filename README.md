# NeuroRead (CAD variant): adaptive phonics tutor prototype

> This is a one-commit snapshot (6 Apr 2026) of an earlier NeuroRead variant, kept for reference. The maintained project is **[NEUROREAD](https://github.com/panshularora/NEUROREAD)**.

NeuroRead is a reading-practice prototype for dyslexic children. It picks the next exercise with classical learner models, and it simplifies text with an LLM that is checked by a validation step.

## What is in the code
| Area | Implementation | Where |
|---|---|---|
| Skill tracking | Bayesian Knowledge Tracing (Corbett & Anderson, 1994) with fixed parameters | `backend/app/services/learning/bkt_engine.py` |
| Item scoring | IRT 2PL ability/difficulty estimate | `services/learning/irt_scorer.py` |
| Difficulty pacing | ZPD-style "flow" rule: escalate when accuracy is above ~85%, cool down when below ~70% | `services/learning/session_flow.py`, `routes/learning/flow_api.py` |
| Exercise content | LLM (Groq, Llama 3.3 70B) generation, with a procedural fallback when no API key is set or the call fails | `services/learning/content_generator.py` |
| Text simplification | Groq Llama 3.3 prompt, then sentence splitting and shortening, then validation (MiniLM embedding similarity against a 0.90 threshold, readability and cognitive-load checks), with a Hugging Face Inference fallback (default `Qwen/Qwen2.5-7B-Instruct`) and a small in-memory TTL cache | `services/simplification_engine.py`, `services/assistive/simplifier.py` |
| UI | React + Vite, Zustand, dnd-kit drag-and-drop tiles, Framer Motion, TTS read-aloud, per-letter colour coding (e.g., b/d) | `frontend/` |

The learner models use fixed parameters; nothing is trained from data. The 0.90 similarity figure is a **pass/fail threshold**, not a measured accuracy. No evaluation of simplification quality or learning outcomes has been run.

## Run
```bash
# backend (needs GROQ_API_KEY in backend/.env; HF_TOKEN optional for the fallback)
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0

# frontend
cd frontend && npm install && npm run dev   # http://localhost:5173
```
`requirements.txt` pulls in torch, transformers and sentence-transformers for the validation step, so the install is large.

## Status and known gaps
- No automated tests in this snapshot. The BKT and simplification tests live in NEUROREAD.
- `backend/neuroadapt.db`, `err.txt` and `__pycache__/` are committed and should be removed and git-ignored.
- Not deployed.

## Stack
Python, FastAPI, SQLAlchemy, sentence-transformers, textstat, gTTS, Groq API; React, Vite, Zustand, dnd-kit, Framer Motion.
