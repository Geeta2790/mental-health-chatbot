from sqlalchemy.orm import Session

from app.repositories.memory_repository import (
    create_memory,
    get_user_memories
)


def extract_and_save_memory(
    db: Session,
    user_id: int,
    text: str
):

    lower_text = text.lower()

    if "i prefer short answers" in lower_text:
        return create_memory(
            db=db,
            user_id=user_id,
            memory_type="communication_style",
            content="User prefers short answers."
        )

    if "i prefer breathing exercises" in lower_text:
        return create_memory(
            db=db,
            user_id=user_id,
            memory_type="wellness_preference",
            content="User prefers breathing exercises."
        )

    return None


def build_memory_context(
    db: Session,
    user_id: int,
    limit: int = 10
):

    memories = get_user_memories(
        db=db,
        user_id=user_id,
        limit=limit
    )

    if not memories:
        return ""

    return "\n".join(
        f"- {m.content}" for m in memories
    )
