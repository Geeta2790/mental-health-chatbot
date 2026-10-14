from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User

from pydantic import BaseModel

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


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    from app.repositories.conversation_repository import get_conversation
    from app.models.message import Message
    from app.models.feedback import Feedback
    from fastapi import HTTPException

    conversation = get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    message_ids = [
        m.id for m in db.query(Message.id)
        .filter(Message.conversation_id == conversation_id).all()
    ]

    if message_ids:
        db.query(Feedback).filter(
            Feedback.message_id.in_(message_ids)
        ).delete(synchronize_session=False)
        db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete(synchronize_session=False)

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted."}


class EditMessageRequest(BaseModel):
    content: str


@router.put("/messages/{message_id}/edit-and-regenerate")
def edit_and_regenerate(
    message_id: int,
    request: EditMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    from app.models.message import Message
    from app.models.feedback import Feedback
    from app.repositories.conversation_repository import get_conversation
    from fastapi import HTTPException

    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    if message.role != "user":
        raise HTTPException(status_code=400, detail="Only user messages can be edited.")

    conversation = get_conversation(
        db=db,
        conversation_id=message.conversation_id,
        user_id=current_user.id
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    doomed_ids = [
        m.id for m in db.query(Message.id)
        .filter(
            Message.conversation_id == conversation.id,
            Message.id >= message_id
        ).all()
    ]

    if doomed_ids:
        db.query(Feedback).filter(
            Feedback.message_id.in_(doomed_ids)
        ).delete(synchronize_session=False)
        db.query(Message).filter(
            Message.id.in_(doomed_ids)
        ).delete(synchronize_session=False)
        db.commit()

    return process_chat(
        db=db,
        user_id=current_user.id,
        question=request.content,
        conversation_id=conversation.id
    )
