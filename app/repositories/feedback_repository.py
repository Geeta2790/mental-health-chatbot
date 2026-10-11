from sqlalchemy.orm import Session

from app.models.feedback import Feedback


def create_feedback(
    db: Session,
    user_id: int,
    message_id: int,
    rating: str,
    comment: str | None = None
):

    feedback = Feedback(
        user_id=user_id,
        message_id=message_id,
        rating=rating,
        comment=comment
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback
