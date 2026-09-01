from sqlalchemy import Column, BigInteger, String, Integer, Float, DateTime
from app.core.database import Base

class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False, index=True)
    frequency = Column(Integer, nullable=False)
    velocity = Column(Float, nullable=False)
    sentiment_bias = Column(String(32), nullable=True)
    timestamp_bucket = Column(DateTime(timezone=True), nullable=False, index=True)