import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.post import Post

def extract_hashtags_and_keywords(text: str) -> list[str]:
    tags = re.findall(r"#\w+", text)
    return [t.lower() for t in tags]

def compute_trend_velocity(db: Session) -> list[dict]:
    # Retrieve latest post timestamp as the baseline reference
    latest_post = db.query(Post).order_by(Post.created_at.desc()).first()
    
    if not latest_post:
        return []

    # Use the most recent activity timestamp instead of static wall-clock time
    ref_time = latest_post.created_at
    t_mid = ref_time - timedelta(hours=2)
    t_start = ref_time - timedelta(hours=4)
    
    # Recent window posts (T0)
    recent_posts = db.query(Post).filter(Post.created_at >= t_mid).all()
    # Past window posts (T-1)
    past_posts = db.query(Post).filter(Post.created_at >= t_start, Post.created_at < t_mid).all()
    
    recent_counts = Counter()
    for p in recent_posts:
        recent_counts.update(extract_hashtags_and_keywords(p.text))
        
    past_counts = Counter()
    for p in past_posts:
        past_counts.update(extract_hashtags_and_keywords(p.text))
        
    all_topics = set(recent_counts.keys()).union(set(past_counts.keys()))
    trends = []
    
    for topic in all_topics:
        c_recent = recent_counts.get(topic, 0)
        c_past = past_counts.get(topic, 0)
        
        if c_past == 0 and c_recent > 0:
            velocity_pct = float(c_recent * 100)
        elif c_past == 0 and c_recent == 0:
            velocity_pct = 0.0
        else:
            velocity_pct = round(((c_recent - c_past) / c_past) * 100.0, 1)
            
        trends.append({
            "topic": topic,
            "frequency": c_recent + c_past,
            "current_window_count": c_recent,
            "past_window_count": c_past,
            "velocity_percentage": velocity_pct,
            "status": "surging" if velocity_pct >= 50 else ("rising" if velocity_pct > 0 else "declining")
        })
        
    return sorted(trends, key=lambda x: (x["velocity_percentage"], x["frequency"]), reverse=True)[:5]