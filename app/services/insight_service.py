def generate_ai_insight_summary(
    sentiment_stats: dict,
    top_trend: dict,
    top_influencer: dict,
    demographics: dict
) -> str:
    dominant_sentiment = "neutral"
    dominant_pct = 0.0
    if sentiment_stats:
        dominant_sentiment, dominant_pct = max(
            sentiment_stats.items(),
            key=lambda item: item[1]
        )

    topic = top_trend.get("topic", "emerging themes")
    velocity = top_trend.get("velocity_percentage", 0.0)
    top_author = top_influencer.get("id", "Key opinion leaders")
    
    # Extract dominant demographic bracket
    age_dist = demographics.get("age_distribution", {})
    dominant_age = max(age_dist.items(), key=lambda item: item[1])[0] if age_dist else "General audience"
    
    geo_dist = demographics.get("geographic_distribution", {})
    dominant_geo = max(geo_dist.items(), key=lambda item: item[1])[0] if geo_dist else "Global"

    summary = (
        f"Real-time monitoring across platforms reveals an overall {dominant_sentiment.upper()} sentiment bias ({dominant_pct}%). "
        f"Discussions are heavily driven by '{topic}', exhibiting a {velocity}% growth velocity. "
        f"Audience profiling identifies primary engagement from {dominant_age} localized in {dominant_geo}. "
        f"Network analysis shows {top_author} acting as the critical propagation node connecting cross-community discussions."
    )
    return summary