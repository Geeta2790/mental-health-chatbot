from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.state import ChatState

from app.rag.retriever import retrieve_documents
from app.rag.generator import generate_answer

from app.repositories.conversation_repository import (
    create_conversation,
    get_conversation
)

from app.repositories.message_repository import (
    create_message,
    get_recent_messages
)

from app.services.memory_service import (
    build_memory_context,
    extract_and_save_memory
)

from app.services.safety_service import (
    classify_safety,
    get_safety_response,
    SafetyCategory
)


UNSAFE_PHRASES = [
    "you have depression",
    "you have anxiety disorder",
    "you are depressed",
    "i diagnose",
    "take this medicine",
    "take this medication",
    "you should take"
]


def ensure_conversation_node(db: Session):

    def node(state: ChatState) -> ChatState:

        user_id = state["user_id"]
        conversation_id = state.get("conversation_id")
        question = state["question"]

        if conversation_id is None:

            conversation = create_conversation(
                db=db,
                user_id=user_id,
                title=question[:50]
            )

        else:

            conversation = get_conversation(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id
            )

            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        return {
            **state,
            "conversation_id": conversation.id
        }

    return node


def load_memory_node(db: Session):

    def node(state: ChatState) -> ChatState:

        conversation_id = state["conversation_id"]

        previous_messages = get_recent_messages(
            db=db,
            conversation_id=conversation_id,
            limit=6
        )

        chat_history = "\n".join(
            f"{m.role}: {m.content}"
            for m in previous_messages
        )

        user_memory = build_memory_context(
            db=db,
            user_id=state["user_id"]
        )

        return {
            **state,
            "chat_history": chat_history,
            "user_memory": user_memory
        }

    return node


def classify_query_node(state: ChatState) -> ChatState:

    category = classify_safety(state["question"])

    return {
        **state,
        "safety_category": category
    }


def safety_response_node(db: Session):

    def node(state: ChatState) -> ChatState:

        answer = get_safety_response(
            category=state["safety_category"]
        )

        create_message(
            db=db,
            conversation_id=state["conversation_id"],
            role="user",
            content=state["question"]
        )

        assistant_message = create_message(
            db=db,
            conversation_id=state["conversation_id"],
            role="assistant",
            content=answer
        )

        return {
            **state,
            "answer": answer,
            "validated_answer": answer,
            "assistant_message_id": assistant_message.id
        }

    return node


def rewrite_query_node(state: ChatState) -> ChatState:

    return state


def retrieve_node(state: ChatState) -> ChatState:

    documents = retrieve_documents(
        query=state["question"],
        top_k=5,
        score_threshold=0.35
    )

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    seen = []
    for doc in documents:
        source = (doc.metadata or {}).get("source")
        if source and source not in seen:
            seen.append(source)

    return {
        **state,
        "retrieved_documents": documents,
        "context": context,
        "sources": seen
    }


def rerank_node(state: ChatState) -> ChatState:

    return state


def generate_node(state: ChatState) -> ChatState:

    if not state.get("retrieved_documents"):

        answer = (
            "I don't have enough relevant information "
            "in my knowledge base to answer that."
        )

        return {
            **state,
            "answer": answer
        }

    answer = generate_answer(
        query=state["question"],
        chat_history=state.get("chat_history", ""),
        user_memory=state.get("user_memory", "")
    )

    return {
        **state,
        "answer": answer
    }


def validate_answer_node(state: ChatState) -> ChatState:

    answer = state["answer"]
    lower = answer.lower()

    for phrase in UNSAFE_PHRASES:
        if phrase in lower:
            return {
                **state,
                "validated_answer": (
                    "I can share general wellness information, "
                    "but I can't diagnose or prescribe. "
                    "Please speak with a qualified mental health professional."
                )
            }

    return {
        **state,
        "validated_answer": answer
    }


def save_conversation_node(db: Session):

    def node(state: ChatState) -> ChatState:

        create_message(
            db=db,
            conversation_id=state["conversation_id"],
            role="user",
            content=state["question"]
        )

        assistant_message = create_message(
            db=db,
            conversation_id=state["conversation_id"],
            role="assistant",
            content=state["validated_answer"],
            sources=state.get("sources") or None
        )

        return {
            **state,
            "assistant_message_id": assistant_message.id
        }

    return node


def update_memory_node(db: Session):

    def node(state: ChatState) -> ChatState:

        extract_and_save_memory(
            db=db,
            user_id=state["user_id"],
            text=state["question"]
        )

        return state

    return node


def route_after_classify(state: ChatState) -> str:

    if state["safety_category"] == SafetyCategory.NORMAL:
        return "normal"

    return "risky"
