from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard Intelligence"])

@router.get("/timeline", summary="Hourly Aggregated Sentiment and Volume Timeline")
def get_timeline_metrics(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            date_trunc('hour', p.created_at) AS time_bucket,
            COUNT(p.id) AS total_posts,
            COUNT(CASE WHEN s.sentiment = 'positive' THEN 1 END) AS positive_count,
            COUNT(CASE WHEN s.sentiment = 'negative' THEN 1 END) AS negative_count,
            COUNT(CASE WHEN s.sentiment = 'neutral' THEN 1 END) AS neutral_count
        FROM posts p
        LEFT JOIN sentiment_results s ON p.id = s.post_id
        GROUP BY time_bucket
        ORDER BY time_bucket ASC;
    """)
    
    rows = db.execute(query).fetchall()
    timeline = [
        {
            "timestamp": row.time_bucket.isoformat() if row.time_bucket else None,
            "total_posts": row.total_posts,
            "positive": row.positive_count,
            "negative": row.negative_count,
            "neutral": row.neutral_count,
        }
        for row in rows
    ]
    return {"timeline": timeline}