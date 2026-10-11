from pathlib import Path

from app.rag.retriever import get_vector_store
from app.services.document_service import ingest_document


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def existing_sources() -> set[str]:

    vector_store = get_vector_store()
    client = vector_store.client
    collection = vector_store.collection_name

    sources: set[str] = set()
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=1000,
            offset=offset,
            with_payload=True
        )
        for point in points:
            metadata = (point.payload or {}).get("metadata") or {}
            source = metadata.get("source")
            if source:
                sources.add(source)
        if offset is None:
            break

    return sources


def seed():

    if not DATA_DIR.exists():
        print(f"No data directory at {DATA_DIR}")
        return

    already_indexed = existing_sources()

    for file_path in sorted(DATA_DIR.iterdir()):

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        filename = file_path.name

        if filename in already_indexed:
            print(f"Skip (already indexed): {filename}")
            continue

        print(f"Ingesting: {filename}")

        result = ingest_document(
            file_path=str(file_path),
            filename=filename
        )

        print(f"  -> chunks created: {result['chunks_created']}")


if __name__ == "__main__":
    seed()
