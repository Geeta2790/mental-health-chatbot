from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.db.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    message_id = Column(
        Integer,
        ForeignKey("messages.id"),
        nullable=False,
        index=True
    )

    rating = Column(
        String,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
