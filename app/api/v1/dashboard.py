from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.post import Post
from app.models.sentiment import SentimentResult
from app.services.network_service import compute_graph_analytics
from app.services.trend_service import compute_trend_velocity
from app.services.demographic_service import compute_demographics_breakdown
from app.services.insight_service import generate_ai_insight_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard Intelligence"])

@router.get("/overview", summary="Unified 5-Vector SIH Analytics Payload")
def get_dashboard_overview(db: Session = Depends(get_db)):
    # 1. Total Metrics
    total_posts = db.query(func.count(Post.id)).scalar() or 0
    
    # 2. Sentiment Aggregation
    sentiment_rows = db.query(SentimentResult.sentiment, func.count(SentimentResult.post_id)).group_by(SentimentResult.sentiment).all()
    sent_total = sum(c for _, c in sentiment_rows) or 1
    sentiment_dist = {s: round((c / sent_total) * 100, 1) for s, c in sentiment_rows}
    
    # 3. Trends & Velocity
    trends = compute_trend_velocity(db)
    
    # 4. Network Topology & Graph Metrics
    network_data = compute_graph_analytics(db)
    
    # 5. Demographics
    demographics = compute_demographics_breakdown(db)
    
    # 6. AI Insight Synthesis
    ai_summary = generate_ai_insight_summary(
        sentiment_stats=sentiment_dist,
        top_trend=trends[0] if trends else {},
        top_influencer=network_data["top_influencers"][0] if network_data["top_influencers"] else {},
        demographics=demographics
    )
    
    return {
        "summary_metrics": {
            "total_posts_ingested": total_posts,
            "total_nodes_mapped": len(network_data["nodes"]),
            "total_edges_connected": len(network_data["edges"])
        },
        "sentiment_distribution": sentiment_dist,
        "trending_topics": trends,
        "demographics_breakdown": demographics,
        "network_topology": network_data,
        "ai_executive_summary": ai_summary
    }