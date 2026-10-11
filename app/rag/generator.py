from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.rag.retriever import retrieve_documents

load_dotenv()


def generate_answer(
    query: str,
    chat_history: str = "",
    user_memory: str = ""
):

    documents = retrieve_documents(
        query=query,
        top_k=5,
        score_threshold=0.35
    )

    if not documents:
        return (
            "I don't have enough relevant information "
            "in my knowledge base to answer that."
        )

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    prompt = f"""You are a mental wellness assistant.

Rules:
- Answer using the provided knowledge context.
- Use conversation history only to understand the current conversation.
- Use user memory only for personalization.
- Do not treat user memory as medical facts.
- Do not diagnose the user.
- Do not prescribe medication.
- If the knowledge context does not contain enough information, say:
  "I don't have enough information in my knowledge base to answer that."

User Preferences / Memory:
{user_memory}

Conversation History:
{chat_history}

Knowledge Context:
{context}

Current User Question:
{query}

Answer:
"""

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    question = "how to improve my mental health"

    answer = generate_answer(question)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)
