import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class CredibilityResult(Base):
    """
    Misinformation-RISK triage signal for a post -- NOT a fact-check verdict.

    This intentionally never stores a "true"/"false" label. It stores an
    explainable 0-100 risk score built from (a) a pretrained fake-news
    language model's probability estimate and (b) transparent linguistic
    heuristics (sensationalism markers, missing source attribution, etc.),
    meant to help a human analyst triage which posts are worth a closer
    look or an actual fact-check -- consistent with CivicShield's
    "explainable indicator for human review" design principle.
    """
    __tablename__ = "credibility_results"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    misinformation_risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String(16), nullable=False)            # Low / Moderate / Elevated / High
    sensationalism_score = Column(Float, nullable=False)       # 0-100, heuristic-only sub-score
    model_fake_probability = Column(Float, nullable=True)      # 0-1, from HF fake-news model
    contributing_factors = Column(JSONB, default=dict)
    model_version = Column(String(32), default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
