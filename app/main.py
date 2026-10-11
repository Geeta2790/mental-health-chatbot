from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as document_router


app = FastAPI(
    title="WellMind AI",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(document_router)


@app.get("/")
def home():

    return {
        "message": "WellMind AI is running"
    }
