from app.database import SessionLocal
from app.models.user import UserProfile


def update_user_profile(user_id: str, level: int, score: float):
    db = SessionLocal()

    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if user:
        user.preferred_level = level
        user.last_score = score
        user.total_sessions += 1

        # Rolling average update
        if user.total_sessions > 1:
            user.avg_cognitive_score = (
                (user.avg_cognitive_score * (user.total_sessions - 1)) + score
            ) / user.total_sessions
        else:
            user.avg_cognitive_score = score

    else:
        user = UserProfile(
            user_id=user_id,
            preferred_level=level,
            avg_cognitive_score=score,
            last_score=score,
            total_sessions=1
        )
        db.add(user)

    db.commit()
    db.close()