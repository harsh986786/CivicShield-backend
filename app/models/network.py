from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class NetworkEdge(Base):
    __tablename__ = "network_edges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_author_id = Column(String(255), nullable=False, index=True)
    target_author_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(32), nullable=False)
    interaction_type = Column(String(32), nullable=False)  # reply, mention, repost
    created_at = Column(DateTime(timezone=True), nullable=False)