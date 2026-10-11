from sqlalchemy.orm import Session

from app.models.message import Message


def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    sources: list[str] | None = None
):

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int
):

    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )


def get_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 6
):

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    return list(reversed(messages))