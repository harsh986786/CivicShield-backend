from sqlalchemy import Column, BigInteger, String, Float, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class CivicEvent(Base):
    """
    Geo-tagged real-world signal from an external event/news source (currently GDELT).

    This is intentionally kept separate from `posts` (social media) because it
    represents a different signal type -- news-coverage geography and tone,
    not individual social posts -- but shares the same region vocabulary
    (app.services.geo_service) so it can be fused with social data for the
    civic-risk layer.
    """
    __tablename__ = "civic_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source = Column(String(32), nullable=False, default="gdelt")
    query_used = Column(String(255), nullable=False)
    location_name = Column(String(255), nullable=True)
    region = Column(String(64), nullable=True, index=True)  # matched via geo_service
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    mention_count = Column(Integer, default=0)
    avg_tone = Column(Float, nullable=True)  # GDELT tone score; negative = more negative coverage
    sample_headline = Column(Text, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
