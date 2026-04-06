# Learning Mode – Design & Implementation

Dyslexia-focused learning system for children (ages 4–10): adaptive engine, session/exercise flow, and UI.

---

## 1. Folder structure

```
backend/
├── app/
│   ├── main.py                    # Mounts learning session router
│   ├── database.py
│   ├── models/
│   │   ├── user.py
│   │   └── child_learner.py       # ChildLearner: child_id, age, learning_level, error_patterns, progress_metrics
│   ├── routes/
│   │   ├── learning/
│   │   │   ├── session.py         # POST /session/start, GET /exercise/next, POST /response/submit, GET /progress, GET /recommendations
│   │   │   ├── phonics.py
│   │   │   ├── spelling.py
│   │   │   └── exercises.py
│   │   └── ...
│   └── services/
│       └── learning/
│           ├── adaptive_engine.py   # Error patterns, difficulty scaling, recommendations
│           ├── content_engine.py     # Words, letters, sentences by difficulty
│           ├── session_engine.py     # Start session, next exercise, submit response
│           ├── learner_repo.py       # Get/create ChildLearner, update after session
│           ├── phonics_engine.py
│           ├── spelling_trainer.py
│           └── ...
frontend/
├── src/
│   ├── components/
│   │   ├── LearningMode.jsx        # Container: dashboard vs module view
│   │   └── learning/
│   │       ├── LearningDashboard.tsx  # Daily mission, XP bar, 4 cards
│   │       ├── ModulePhonics.tsx
│   │       ├── ModuleSpelling.tsx
│   │       ├── ModuleComprehension.tsx
│   │       └── ModuleReading.tsx
│   ├── services/
│   │   └── api.ts                  # sessionStart, exerciseNext, responseSubmit, getLearningProgress, getRecommendations
│   └── types/
│       └── apiTypes.ts             # SessionStartResponse, LearningExercise, SubmitResponseResult, LearningProgressResponse
```

---

## 2. API design (REST)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/session/start` | Body: `{ child_id, age? }`. Start session; returns `session_id`, first `exercise`. |
| GET | `/exercise/next` | Query: `session_id`. Get next exercise (e.g. after refresh). |
| POST | `/response/submit` | Body: `session_id, exercise_id, is_correct, response?, expected?, actual?`. Submit answer; returns feedback, `xp_delta`, `next_exercise` or completion + `recommendations`. |
| GET | `/progress` | Query: `child_id`. Returns XP, level, streak, `error_patterns`, `progress_metrics`, `recommendations`. |
| GET | `/recommendations` | Query: `child_id`. Returns smart recommendations only. |

---

## 3. Adaptive learning algorithm (explained)

### 3.1 Error pattern detection

- **Stored:** `error_patterns` is a JSON map: `pattern_id → error rate (0–1)`.
- **Confusion pairs:** We track e.g. `b_d_confusion`, `p_q_confusion`, `m_n_confusion`.
- **When user is wrong:** If expected letter was `b` and actual was `d`, we increment `b_d_confusion` (capped).
- **Threshold:** If any pattern rate ≥ `CONFUSION_THRESHOLD` (0.35), we set a **focus** (e.g. `b_d_confusion`).
- **Content effect:** Content engine uses this focus to serve more b/d (or p/q, etc.) in phonics and spelling.

### 3.2 Difficulty scaling

- **Levels:** 1 = letters / very easy, 2 = words / medium, 3 = sentences / hard.
- **Inputs:** `current_level`, `recent_success_rate`, `recent_attempts`.
- **Rules:**
  - If `recent_attempts >= MIN_ATTEMPTS_FOR_LEVEL_CHANGE` (5):
    - If `recent_success_rate >= SUCCESS_RATE_UP` (0.75) and `current_level < 3` → **level up**.
    - If `recent_success_rate <= SUCCESS_RATE_DOWN` (0.45) and `current_level > 1` → **level down**.
  - Otherwise keep `current_level`.

### 3.3 Reinforcement loop

- **Weak areas:** High error rate in a confusion pattern → that pattern is chosen as **focus** → content engine serves more of that pair (e.g. b/d).
- **Strong areas:** Low error rate → no focus for that pair → normal mix of content.
- **Module weights (optional):** `reinforcement_weights(error_patterns, module)` can weight how often to show phonics/spelling vs comprehension/reading based on need.

### 3.4 Smart recommendations

- **Confusion-based:** If any pattern ≥ threshold → add “Practice X vs Y distinction”.
- **Weakest module:** Sort `progress_metrics` by value; recommend “Spend more time on &lt;module&gt;”.
- **Level tip:** Level 1 → “Focus on short vowel sounds”; Level 2 → “Practice building simple words”; Level 3 → “Try reading short sentences aloud”.

---

## 4. Example data flow

1. **Start session:**  
   `POST /session/start` with `child_id`.  
   Backend loads ChildLearner (or creates), reads `learning_level`, `error_patterns`, `progress_metrics`.  
   Session engine creates in-memory session, picks first exercise (e.g. phonics with b/d focus if `b_d_confusion` high).  
   Response: `session_id`, `exercise` (e.g. `{ type: "phonics", letters: [...] }`).

2. **Submit response:**  
   `POST /response/submit` with `session_id`, `exercise_id`, `is_correct`, optional `expected`/`actual` for letter confusions.  
   Engine updates session’s `recent_successes`/`recent_attempts`, updates `error_patterns` if it was a letter confusion.  
   Computes next difficulty (level up/down).  
   Generates next exercise (or “complete”) and, on completion, recommendations.  
   Persists learner state (level, error_patterns, XP) via `update_learner_after_session`.

3. **Progress / recommendations:**  
   `GET /progress?child_id=...` or `GET /recommendations?child_id=...`  
   Load ChildLearner, parse JSON fields, run `get_recommendations(...)`, return.

---

## 5. Frontend behaviour

- **Dashboard:** Daily mission (from first focus recommendation), XP, level, streak, progress bar; 4 cards with progress % and hover/click (Framer Motion).
- **Cards:** Interactive Phonics, Spelling Trainer, Comprehension Lab, Guided Reading → each opens a **module page** (Phonics: letter tap + sound + waveform; Spelling: drag/shuffle + check; Comprehension: MCQ + feedback; Reading: tap word → TTS, speed control).
- **Theme:** Dark (charcoal), soft orange (clay) accents, OpenDyslexic, minimal cognitive load.

---

## 6. Future improvements

- **Persistence:** Replace in-memory `_sessions` with **Redis** (session store + cache) for multi-instance and low-latency.
- **Speech:** Integrate **Whisper** or **Vosk** for voice input; score pronunciation vs expected phoneme for spelling/phonics.
- **Content:** Expand word banks and comprehension passages; add difficulty tags and more MCQ options from a content CMS.
- **Analytics:** Parent dashboard: error pattern trends, time per module, level progression over time.
- **Gamification:** Badges, daily streak logic (e.g. `last_activity_date`), unlockable avatars.
- **Accessibility:** Full keyboard/screen-reader support; optional larger touch targets and reduced motion.
- **A/B tests:** Compare level-up thresholds and confusion thresholds to tune engagement and learning gain.
