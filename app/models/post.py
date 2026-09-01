import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(32), nullable=False, index=True)
    platform_post_id = Column(String(255), nullable=False)
    author_id = Column(String(255), nullable=False)
    author_username = Column(String(255), nullable=True)
    author_bio = Column(Text, nullable=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    parent_post_id = Column(String(255), nullable=True)
    engagement_count = Column(JSONB, default=dict)
    raw_data = Column(JSONB, default=dict)
    is_processed = Column(Boolean, default=False, index=True)

    __table_args__ = (
        UniqueConstraint("platform", "platform_post_id", name="uq_platform_post"),
    )