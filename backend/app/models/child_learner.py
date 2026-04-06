"""
Child learner model for dyslexia-focused Learning Mode (ages 4–10).

Stores learning level, error patterns (e.g. b/d confusion), and progress metrics
for the adaptive learning engine.
"""
from __future__ import annotations

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ChildLearner(Base):
    __tablename__ = "child_learners"

    # Identity
    child_id = Column(String(64), primary_key=True, index=True)

    # Demographics (for age-appropriate content)
    age = Column(Integer, default=6)  # 4–10

    # Learning level: 1=letter, 2=word, 3=sentence (maps to difficulty tiers)
    learning_level = Column(Integer, default=1)

    # XP and gamification
    total_xp = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(String(10), default=None)  # YYYY-MM-DD

    # Error patterns: JSON string e.g. {"b_d_confusion": 0.7, "p_q_confusion": 0.3, "short_vowels": 0.5}
    # Keys are pattern IDs; values are error rate (0–1) or count depending on strategy.
    error_patterns = Column(Text, default="{}")

    # Progress metrics: JSON e.g. {"phonics": 0.6, "spelling": 0.4, "comprehension": 0.5, "reading": 0.3}
    progress_metrics = Column(Text, default="{}")

    # Session state: current session_id if in progress (for GET /exercise/next)
    current_session_id = Column(String(64), default=None)
    current_session_started_at = Column(DateTime(timezone=True), default=None, onupdate=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
