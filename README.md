# NeuroRead: Adaptive AI Tutoring System

NeuroRead is a highly advanced, research-grade multimodal phonic reading platform designed specifically for dyslexic children (ages 4-12). It replaces traditional "rule-based" test engines with an autonomous, continuous learning environment that adapts mathematically to a child's struggles and breakthroughs.

## 🚀 Core Features

### 1. Bayesian Knowledge Tracing (BKT)
Uses a Hidden Markov Model (Corbett & Anderson, 1994) to probabilistically calculate a child's conceptual understanding based on item slips and learning transitions, instead of relying on a simple percentage score.

### 2. Item Response Theory (IRT - 2PL)
Calibrates item difficulty and the child's true cognitive ability on a continuous scale, seamlessly ignoring false negatives and adjusting to reaction times.

### 3. Vygotsky's Zone of Proximal Development (ZPD)
Maintains a continuous "flow state." If accuracy runs too high (>85%), it identifies boredom and escalates phase. If time increases and accuracy drops (<70%), it flags "anxiety" and triggers cooldown periods.

### 4. Multimodal Perceptual Engine
Text is completely interactive, supporting continuous drag-and-drop tiles and text-to-speech auto-reading. Reverses dyslexic character-inversion via constant mapping (`b` returns blue, `p` returns purple).

---

## 🛠️ Tech Stack

*   **Frontend**: React, Vite, Tailwind CSS, Framer Motion, Zustand (State), DND-Kit.
*   **Backend**: Python, FastAPI, NumPy/Machine Learning Standard Library.
*   **Generative AI**: Groq (Llama Models) for Content Generation and Diagnostic Feedback.

---

## 💻 Running the Project Locally

### 1. Run the Backend (FastAPI + AI Brain)
Navigate into the backend and start the Uvicorn server:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```
> Ensure you have created a `.env` in the backend containing your `GROQ_API_KEY`.

### 2. Run the Frontend (React UI)
Navigate into the frontend and start the Vite dev server:
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
Navigate to `http://localhost:5173` and launch **Learning Mode** to interact directly with the continuous tutor loop.

---

*Prepared by Senior Engineering for Production Demo.*
