from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.post import Post
from app.models.sentiment import SentimentResult

router = APIRouter(prefix="/network", tags=["Network & Link Analysis"])

@router.get("/propagation-timeline", summary="Track chronological diffusion of discussions through influencers")
def get_propagation_timeline(topic: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    query = (
        db.query(Post, SentimentResult)
        .outerjoin(SentimentResult, Post.id == SentimentResult.post_id)
        .order_by(Post.created_at.asc())
    )
    
    if topic:
        query = query.filter(Post.text.ilike(f"%{topic}%"))
        
    results = query.limit(limit).all()
    
    cascade_events = []
    for post, sentiment in results:
        cascade_events.append({
            "timestamp": post.created_at.isoformat(),
            "platform": post.platform,
            "author_id": post.author_id,
            "parent_post_id": post.parent_post_id,
            "sentiment": sentiment.sentiment if sentiment else "neutral",
            "emotion": sentiment.emotion if sentiment else "neutral",
            "snippet": post.text[:80]
        })
        
    return {
        "filtered_topic": topic or "all_topics",
        "total_cascade_steps": len(cascade_events),
        "cascade_flow": cascade_events
    }