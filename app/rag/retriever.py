from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
QDRANT_PATH = BASE_DIR / "qdrant_db"

_vector_store = None


def get_vector_store():

    global _vector_store

    if _vector_store is None:

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        _vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            path=str(QDRANT_PATH),
            collection_name="mental_health_docs"
        )

    return _vector_store


def retrieve_documents(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.35
):

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        query=query,
        k=top_k
    )

    relevant_documents = []

    for document, score in results:
        print(
            f"Score: {score:.4f} | "
            f"Text: {document.page_content[:80]}"
        )
        if score >= score_threshold:
            relevant_documents.append(document)

    return relevant_documents


if __name__ == "__main__":

    question = "What can help with anxiety?"

    documents = retrieve_documents(
        query=question,
        top_k=5,
        score_threshold=0.35
    )

    print("\nAccepted documents:")

    for index, doc in enumerate(
        documents,
        start=1
    ):
        print(f"\n--- {index} ---")
        print(doc.page_content)
