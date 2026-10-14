from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.agents.state import ChatState

from app.agents.nodes import (
    ensure_conversation_node,
    load_memory_node,
    classify_query_node,
    safety_response_node,
    smalltalk_response_node,
    rewrite_query_node,
    retrieve_node,
    rerank_node,
    generate_node,
    validate_answer_node,
    save_conversation_node,
    update_memory_node,
    route_after_classify
)


def build_chat_graph(db: Session):

    graph = StateGraph(ChatState)

    graph.add_node(
        "ensure_conversation",
        ensure_conversation_node(db)
    )
    graph.add_node(
        "load_memory",
        load_memory_node(db)
    )
    graph.add_node(
        "classify_query",
        classify_query_node
    )
    graph.add_node(
        "safety_response",
        safety_response_node(db)
    )
    graph.add_node(
        "smalltalk_response",
        smalltalk_response_node(db)
    )
    graph.add_node(
        "rewrite_query",
        rewrite_query_node
    )
    graph.add_node(
        "retrieve",
        retrieve_node
    )
    graph.add_node(
        "rerank",
        rerank_node
    )
    graph.add_node(
        "generate",
        generate_node
    )
    graph.add_node(
        "validate_answer",
        validate_answer_node
    )
    graph.add_node(
        "save_conversation",
        save_conversation_node(db)
    )
    graph.add_node(
        "update_memory",
        update_memory_node(db)
    )

    graph.add_edge(START, "ensure_conversation")
    graph.add_edge("ensure_conversation", "load_memory")
    graph.add_edge("load_memory", "classify_query")

    graph.add_conditional_edges(
        "classify_query",
        route_after_classify,
        {
            "normal": "rewrite_query",
            "risky": "safety_response",
            "smalltalk": "smalltalk_response"
        }
    )

    graph.add_edge("rewrite_query", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", "validate_answer")
    graph.add_edge("validate_answer", "save_conversation")
    graph.add_edge("save_conversation", "update_memory")
    graph.add_edge("update_memory", END)

    graph.add_edge("safety_response", END)
    graph.add_edge("smalltalk_response", END)

    return graph.compile()
