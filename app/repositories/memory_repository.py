from sqlalchemy.orm import Session

from app.models.user_memory import UserMemory


def create_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    content: str
):

    memory = UserMemory(
        user_id=user_id,
        memory_type=memory_type,
        content=content
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def get_user_memories(
    db: Session,
    user_id: int,
    limit: int = 10
):

    return (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .order_by(UserMemory.created_at.desc())
        .limit(limit)
        .all()
    )
