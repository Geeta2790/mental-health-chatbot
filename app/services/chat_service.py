from sqlalchemy.orm import Session

from app.agents.graph import build_chat_graph


def process_chat(
    db: Session,
    user_id: int,
    question: str,
    conversation_id: int | None = None
):

    graph = build_chat_graph(db=db)

    initial_state = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "question": question
    }

    final_state = graph.invoke(initial_state)

    return {
        "conversation_id": final_state["conversation_id"],
        "message_id": final_state["assistant_message_id"],
        "answer": final_state["validated_answer"],
        "sources": final_state.get("sources") or []
    }
