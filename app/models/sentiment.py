import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    sentiment = Column(String(32), nullable=False)   # positive, negative, neutral
    emotion = Column(String(32), nullable=False)     # anger, joy, sadness, fear, surprise, love
    confidence = Column(Float, nullable=False)
    # Sarcasm/irony is a separate rhetorical-device signal from a real classifier
    # (cardiffnlp/twitter-roberta-base-irony), kept apart from `emotion` so it
    # doesn't overwrite the underlying emotional label -- a sarcastic post can
    # still be angry, joyful, etc.
    is_sarcastic = Column(Boolean, nullable=False, default=False)
    sarcasm_confidence = Column(Float, nullable=True)
    model_version = Column(String(32), default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())