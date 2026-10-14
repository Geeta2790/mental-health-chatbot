from typing import TypedDict, Optional, List, Any

from app.services.safety_service import SafetyCategory


class ChatState(TypedDict, total=False):

    user_id: int
    conversation_id: Optional[int]
    question: str

    chat_history: str
    user_memory: str

    safety_category: SafetyCategory
    is_smalltalk: bool

    retrieved_documents: List[Any]
    context: str
    sources: List[str]

    answer: str
    validated_answer: str
    assistant_message_id: int
