from sqlalchemy import Column, String, Integer, Float
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True, index=True)

    preferred_level = Column(Integer)

    avg_cognitive_score = Column(Float, default=0.0)
    last_score = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)