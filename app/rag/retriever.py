import threading

from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models as qmodels

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
QDRANT_PATH = BASE_DIR / "qdrant_db"
COLLECTION_NAME = "mental_health_docs"
EMBEDDING_DIM = 1536

_vector_store = None
_init_lock = threading.Lock()


def get_vector_store():

    global _vector_store

    if _vector_store is not None:
        return _vector_store

    with _init_lock:

        if _vector_store is not None:
            return _vector_store

        QDRANT_PATH.mkdir(parents=True, exist_ok=True)

        client = QdrantClient(path=str(QDRANT_PATH))

        try:
            if not client.collection_exists(COLLECTION_NAME):
                client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=qmodels.VectorParams(
                        size=EMBEDDING_DIM,
                        distance=qmodels.Distance.COSINE
                    )
                )

            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small"
            )

            _vector_store = QdrantVectorStore(
                client=client,
                collection_name=COLLECTION_NAME,
                embedding=embeddings
            )
        except Exception:
            try:
                client.close()
            except Exception:
                pass
            raise

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
