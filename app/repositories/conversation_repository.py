from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: int,
    title: str | None = None
):

    conversation = Conversation(
        user_id=user_id,
        title=title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    conversation_id: int,
    user_id: int
):

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )


def list_user_conversations(
    db: Session,
    user_id: int,
    limit: int = 50
):

    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .all()
    )