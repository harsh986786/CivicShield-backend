from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.post import Post
from app.models.sentiment import SentimentResult
from app.models.credibility import CredibilityResult

router = APIRouter(prefix="/credibility", tags=["Sarcasm & Misinformation-Risk Signals"])


@router.get("/overview", summary="Aggregate misinformation-risk distribution")
def get_credibility_overview(db: Session = Depends(get_db)):
    total = db.query(func.count(CredibilityResult.post_id)).scalar() or 0

    level_rows = (
        db.query(CredibilityResult.risk_level, func.count(CredibilityResult.post_id))
        .group_by(CredibilityResult.risk_level)
        .all()
    )
    level_dist = {level: count for level, count in level_rows}

    avg_score = db.query(func.avg(CredibilityResult.misinformation_risk_score)).scalar()
    avg_model_prob = db.query(func.avg(CredibilityResult.model_fake_probability)).scalar()

    sarcasm_total = db.query(func.count(SentimentResult.post_id)).filter(
        SentimentResult.is_sarcastic == True
    ).scalar() or 0
    sentiment_total = db.query(func.count(SentimentResult.post_id)).scalar() or 1

    return {
        "disclaimer": (
            "These are explainable RISK/triage signals for human review, not "
            "verdicts. A high score means 'a human fact-checker should look at "
            "this,' not 'this is confirmed false.'"
        ),
        "posts_analyzed": total,
        "risk_level_distribution": level_dist,
        "avg_misinformation_risk_score": round(avg_score, 1) if avg_score else 0.0,
        "avg_model_fake_probability": round(avg_model_prob, 3) if avg_model_prob else None,
        "sarcasm_signal": {
            "flagged_count": sarcasm_total,
            "flagged_pct_of_posts": round((sarcasm_total / sentiment_total) * 100, 1),
        },
    }


@router.get("/flagged", summary="Posts flagged for human fact-check review")
def get_flagged_posts(
    min_score: float = Query(50.0, ge=0, le=100),
    limit: int = Query(25, le=200),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Post, CredibilityResult)
        .join(CredibilityResult, Post.id == CredibilityResult.post_id)
        .filter(CredibilityResult.misinformation_risk_score >= min_score)
        .order_by(CredibilityResult.misinformation_risk_score.desc())
        .limit(limit)
        .all()
    )

    return {
        "disclaimer": "Triage list for human fact-checkers -- not confirmed misinformation.",
        "count": len(rows),
        "flagged_posts": [
            {
                "post_id": str(post.id),
                "platform": post.platform,
                "author_username": post.author_username,
                "text_preview": (post.text[:200] + "...") if len(post.text) > 200 else post.text,
                "created_at": post.created_at,
                "misinformation_risk_score": cred.misinformation_risk_score,
                "risk_level": cred.risk_level,
                "model_fake_probability": cred.model_fake_probability,
                "contributing_factors": cred.contributing_factors,
            }
            for post, cred in rows
        ],
    }


@router.get("/sarcasm-flagged", summary="Posts flagged as sarcastic/ironic")
def get_sarcasm_flagged_posts(limit: int = Query(25, le=200), db: Session = Depends(get_db)):
    rows = (
        db.query(Post, SentimentResult)
        .join(SentimentResult, Post.id == SentimentResult.post_id)
        .filter(SentimentResult.is_sarcastic == True)
        .order_by(SentimentResult.sarcasm_confidence.desc())
        .limit(limit)
        .all()
    )

    return {
        "count": len(rows),
        "sarcastic_posts": [
            {
                "post_id": str(post.id),
                "platform": post.platform,
                "text_preview": (post.text[:200] + "...") if len(post.text) > 200 else post.text,
                "sentiment": sent.sentiment,
                "emotion": sent.emotion,
                "sarcasm_confidence": sent.sarcasm_confidence,
            }
            for post, sent in rows
        ],
    }
