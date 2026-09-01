"""
Civic-risk scoring layer.

IMPORTANT FRAMING (per CivicShield project direction): this score does NOT
predict that any specific event (e.g. a riot) will occur. It is a
transparent, explainable indicator of *abnormal or escalating* signal
patterns in a region -- elevated negative/angry-fearful social sentiment
combined with a rise in geo-tagged unrest-related news coverage -- meant
to help a human analyst decide where to look, not to make a determination
on its own.

The score is a simple weighted sum of named, inspectable factors (NOT a
black-box ML model), by design: explainability was an explicit project
requirement, and a weighted rule-based score is far easier for a human
analyst (or a hackathon judge) to audit and challenge than an opaque
classifier.
"""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.post import Post
from app.models.sentiment import SentimentResult
from app.models.civic_event import CivicEvent
from app.models.credibility import CredibilityResult
from app.services.geo_service import INDIA_REGIONS, UNCLASSIFIED_REGION, match_region_from_text

# Weights sum to 100; each is independently visible in the output so a
# human analyst can see exactly why a region scored the way it did.
WEIGHT_SOCIAL_NEGATIVITY = 20
WEIGHT_ANGER_FEAR = 20
WEIGHT_UNREST_EVENT_DENSITY = 25
WEIGHT_NEWS_TONE = 15
WEIGHT_MISINFORMATION_DENSITY = 20

RISK_NEGATIVE_EMOTIONS = {"anger", "fear"}


def _risk_level(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Elevated"
    if score >= 25:
        return "Moderate"
    return "Low"


def compute_civic_risk_map(db: Session, unrest_lookback_hours: int = 48) -> dict:
    # ---- 1. Social signal: posts + sentiment, bucketed by region via author bio ----
    social_rows = (
        db.query(Post.author_bio, SentimentResult.sentiment, SentimentResult.emotion)
        .join(SentimentResult, Post.id == SentimentResult.post_id)
        .all()
    )

    region_post_totals: dict[str, int] = defaultdict(int)
    region_negative: dict[str, int] = defaultdict(int)
    region_anger_fear: dict[str, int] = defaultdict(int)

    for bio, sentiment, emotion in social_rows:
        region = match_region_from_text(bio) or UNCLASSIFIED_REGION
        region_post_totals[region] += 1
        if sentiment == "negative":
            region_negative[region] += 1
        if emotion in RISK_NEGATIVE_EMOTIONS:
            region_anger_fear[region] += 1

    # ---- 2. Misinformation-risk signal: high-risk posts, bucketed by region via author bio ----
    # Rationale: virally-spread false rumors are a well-documented real-world
    # trigger for civic unrest (e.g. rumor-driven mob violence), so this is a
    # legitimate risk factor, not just a "content quality" metric.
    misinfo_rows = (
        db.query(Post.author_bio, CredibilityResult.misinformation_risk_score)
        .join(CredibilityResult, Post.id == CredibilityResult.post_id)
        .all()
    )
    region_misinfo_total: dict[str, int] = defaultdict(int)
    region_misinfo_flagged: dict[str, int] = defaultdict(int)
    for bio, score in misinfo_rows:
        region = match_region_from_text(bio) or UNCLASSIFIED_REGION
        region_misinfo_total[region] += 1
        if score is not None and score >= 50:  # Elevated or High risk_level threshold
            region_misinfo_flagged[region] += 1

    # ---- 3. Unrest event signal: GDELT-sourced civic_events, bucketed by region ----
    cutoff = datetime.now(timezone.utc) - timedelta(hours=unrest_lookback_hours)
    event_rows = (
        db.query(CivicEvent.region, func.count(CivicEvent.id), func.sum(CivicEvent.mention_count))
        .filter(CivicEvent.fetched_at >= cutoff)
        .group_by(CivicEvent.region)
        .all()
    )
    region_event_count: dict[str, int] = {r or UNCLASSIFIED_REGION: c for r, c, _ in event_rows}
    region_mention_sum: dict[str, int] = {r or UNCLASSIFIED_REGION: (m or 0) for r, _, m in event_rows}
    max_mentions = max(region_mention_sum.values()) if region_mention_sum else 0

    # ---- 4. Global news-tone modifier (applied uniformly; GDELT tone isn't per-region here) ----
    latest_tone_row = (
        db.query(CivicEvent)
        .filter(CivicEvent.avg_tone.isnot(None))
        .order_by(CivicEvent.fetched_at.desc())
        .first()
    )
    global_tone = latest_tone_row.avg_tone if latest_tone_row else None
    # Map tone (~ -10 very negative .. +10 very positive) to a 0-1 risk contribution
    if global_tone is not None:
        tone_risk_fraction = max(0.0, min(1.0, (2.0 - global_tone) / 12.0))
    else:
        tone_risk_fraction = 0.0

    # ---- 5. Combine into an explainable per-region score ----
    all_regions = set(region_post_totals) | set(region_event_count) | set(INDIA_REGIONS.keys())
    all_regions.discard(UNCLASSIFIED_REGION)  # unclassified isn't mappable, report separately

    regions_out = []
    for region in sorted(all_regions):
        posts_total = region_post_totals.get(region, 0)
        neg_ratio = (region_negative.get(region, 0) / posts_total) if posts_total else 0.0
        anger_fear_ratio = (region_anger_fear.get(region, 0) / posts_total) if posts_total else 0.0
        mentions = region_mention_sum.get(region, 0)
        event_density = (mentions / max_mentions) if max_mentions else 0.0
        misinfo_total = region_misinfo_total.get(region, 0)
        misinfo_ratio = (region_misinfo_flagged.get(region, 0) / misinfo_total) if misinfo_total else 0.0

        social_negativity_score = neg_ratio * WEIGHT_SOCIAL_NEGATIVITY
        anger_fear_score = anger_fear_ratio * WEIGHT_ANGER_FEAR
        unrest_density_score = event_density * WEIGHT_UNREST_EVENT_DENSITY
        news_tone_score = tone_risk_fraction * WEIGHT_NEWS_TONE
        misinfo_density_score = misinfo_ratio * WEIGHT_MISINFORMATION_DENSITY

        total_score = round(
            social_negativity_score + anger_fear_score + unrest_density_score
            + news_tone_score + misinfo_density_score, 1
        )

        centroid = INDIA_REGIONS.get(region)
        regions_out.append({
            "region": region,
            "lat": centroid["lat"] if centroid else None,
            "lon": centroid["lon"] if centroid else None,
            "risk_score": total_score,
            "risk_level": _risk_level(total_score),
            "social_post_count": posts_total,
            "unrest_event_count": region_event_count.get(region, 0),
            "unrest_mention_count": mentions,
            "contributing_factors": {
                "social_negativity": {"value_pct": round(neg_ratio * 100, 1), "weighted_score": round(social_negativity_score, 1)},
                "anger_fear_emotion": {"value_pct": round(anger_fear_ratio * 100, 1), "weighted_score": round(anger_fear_score, 1)},
                "unrest_event_density": {"value_pct": round(event_density * 100, 1), "weighted_score": round(unrest_density_score, 1)},
                "news_coverage_tone": {"global_tone_score": global_tone, "weighted_score": round(news_tone_score, 1)},
                "misinformation_density": {"value_pct": round(misinfo_ratio * 100, 1), "flagged_posts": region_misinfo_flagged.get(region, 0), "weighted_score": round(misinfo_density_score, 1)},
            },
        })

    regions_out.sort(key=lambda r: r["risk_score"], reverse=True)

    return {
        "disclaimer": (
            "Explainable early-warning indicator only. This does NOT predict "
            "that any specific event will occur; it surfaces abnormal or "
            "escalating aggregate signal patterns for human analyst review."
        ),
        "unclassified_social_posts": region_post_totals.get(UNCLASSIFIED_REGION, 0),
        "unclassified_unrest_events": region_event_count.get(UNCLASSIFIED_REGION, 0),
        "regions": regions_out,
    }
