import shutil
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from qdrant_client import models as qmodels

from collections import Counter

from app.api.dependencies import require_admin
from app.models.user import User
from app.services.document_service import ingest_document
from app.rag.retriever import get_vector_store


ALLOWED_EXTENSIONS = {".pdf", ".txt"}

UPLOAD_DIRECTORY = Path("uploads")


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin)
):

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    UPLOAD_DIRECTORY.mkdir(exist_ok=True)

    safe_filename = Path(filename).name

    file_path = UPLOAD_DIRECTORY / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = ingest_document(
            file_path=str(file_path),
            filename=safe_filename
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    return {
        "message": "Document uploaded and indexed successfully.",
        **result
    }


@router.delete("/by-source")
def delete_by_source(
    source: str,
    current_user: User = Depends(require_admin)
):

    vector_store = get_vector_store()
    client = vector_store.client
    collection = vector_store.collection_name

    filter_ = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="metadata.source",
                match=qmodels.MatchValue(value=source)
            )
        ]
    )

    before, _ = client.scroll(
        collection_name=collection,
        scroll_filter=filter_,
        limit=1,
        with_payload=False
    )

    if not before:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found with source '{source}'."
        )

    client.delete(
        collection_name=collection,
        points_selector=qmodels.FilterSelector(filter=filter_)
    )

    return {
        "message": f"Deleted chunks with source '{source}'."
    }


@router.get("/sample")
def sample_chunks(
    source: str,
    limit: int = 3,
    current_user: User = Depends(require_admin)
):

    vector_store = get_vector_store()
    client = vector_store.client
    collection = vector_store.collection_name

    filter_ = qmodels.Filter(
        must=[
            qmodels.FieldCondition(
                key="metadata.source",
                match=qmodels.MatchValue(value=source)
            )
        ]
    )

    points, _ = client.scroll(
        collection_name=collection,
        scroll_filter=filter_,
        limit=limit,
        with_payload=True
    )

    return {
        "source": source,
        "samples": [
            (p.payload or {}).get("page_content")
            for p in points
        ]
    }


@router.get("/sources")
def list_sources(
    current_user: User = Depends(require_admin)
):

    vector_store = get_vector_store()
    client = vector_store.client
    collection = vector_store.collection_name

    counts: Counter = Counter()
    total = 0
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=1000,
            offset=offset,
            with_payload=True
        )
        for point in points:
            total += 1
            metadata = (point.payload or {}).get("metadata") or {}
            source = metadata.get("source") or "<no-source metadata>"
            counts[source] += 1
        if offset is None:
            break

    return {
        "total_points": total,
        "sources": [
            {"source": src, "chunks": n}
            for src, n in counts.most_common()
        ]
    }
