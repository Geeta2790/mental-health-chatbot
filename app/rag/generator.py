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

    prompt = f"""You are WellMind, a warm mental wellness assistant.

Style:
- Keep answers short. 2 to 4 sentences for simple questions. Up to 6 for complex ones.
- Use simple, everyday English. Avoid jargon. Write like a thoughtful friend.
- No bullet points, numbered lists, or headings unless the user explicitly asked for steps.
- Match the user's communication style preferences from memory when present.

Rules:
- Base factual claims only on the knowledge context below.
- Use conversation history to understand what the user is referring to.
- Use user memory only for personalization, not as medical fact.
- Do not diagnose. Do not prescribe medication.
- If the knowledge context does not cover the question, say so briefly and warmly, and suggest reframing or seeking a professional if relevant.

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


def generate_followup_answer(
    query: str,
    chat_history: str,
    user_memory: str = ""
):

    prompt = f"""You are WellMind, a warm mental wellness assistant.

The user's current question appears to be a follow-up about the previous conversation, not a new topic covered by the knowledge base.

Style:
- Short: 1 to 3 sentences.
- Simple everyday English. Warm, like a friend.
- No bullet lists or headings.

Rules:
- Base your reply only on the Conversation History below.
- If they ask where information came from, reference the sources tagged in the history.
- Do not invent new factual claims about wellness. Point back to the earlier answer instead.
- If their question is unrelated to wellness, briefly redirect them to mental wellness topics.
- Do not diagnose or prescribe.

User Preferences / Memory:
{user_memory}

Conversation History:
{chat_history}

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
