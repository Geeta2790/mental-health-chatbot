from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse
)

from app.services.chat_service import process_chat
from app.repositories.feedback_repository import create_feedback
from app.repositories.conversation_repository import list_user_conversations
from app.repositories.message_repository import get_conversation_messages


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return process_chat(
        db=db,
        user_id=current_user.id,
        question=request.question,
        conversation_id=request.conversation_id
    )


@router.post(
    "/feedback",
    response_model=FeedbackResponse
)
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    feedback = create_feedback(
        db=db,
        user_id=current_user.id,
        message_id=request.message_id,
        rating=request.rating,
        comment=request.comment
    )

    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating
    )


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversations = list_user_conversations(
        db=db,
        user_id=current_user.id
    )

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat()
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    from app.repositories.conversation_repository import get_conversation
    from fastapi import HTTPException

    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id
    )

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]
