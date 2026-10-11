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
