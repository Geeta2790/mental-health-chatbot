from app.rag.loader import load_document
from app.rag.chunker import chunk_text
from app.rag.retriever import get_vector_store


def ingest_document(
    file_path: str,
    filename: str
):

    text = load_document(file_path)

    if not text.strip():
        raise ValueError(
            "No readable text found in document."
        )

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError(
            "Document produced no chunks."
        )

    metadatas = [
        {
            "source": filename,
            "chunk_id": index
        }
        for index in range(len(chunks))
    ]

    vector_store = get_vector_store()

    vector_store.add_texts(
        texts=chunks,
        metadatas=metadatas
    )

    return {
        "filename": filename,
        "chunks_created": len(chunks)
    }
