from fastapi import APIRouter
from app.database import SessionLocal
from app.models.user import UserProfile

router = APIRouter()


@router.get("/progress/{user_id}")
def get_progress(user_id: str):

    db = SessionLocal()
    user = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not user:
        return {"message": "User not found"}

    return {
        "user_id": user.user_id,
        "preferred_level": user.preferred_level,
        "average_cognitive_score": f"{user.avg_cognitive_score:.2f}",
        "last_score": user.last_score,
        "total_sessions": user.total_sessions
    }