import re
from collections import Counter
from sqlalchemy.orm import Session
from app.models.post import Post
from app.services.geo_service import match_region_from_text, UNCLASSIFIED_REGION

# Geographic inference now delegates to app.services.geo_service, which is
# the single canonical India state/UT gazetteer shared with the civic-risk
# map (app/services/risk_service.py). This keeps "Delhi NCR" etc. consistent
# across demographics and the geo-risk map instead of using two different
# region vocabularies.

AGE_PROFILES = {
    "18-24 (Gen-Z / Students)": ["student", "undergrad", "college", "intern", "cs"],
    "25-34 (Professionals)": ["engineer", "developer", "founder", "manager", "pro", "analyst"],
    "35-50 (Senior Leads)": ["director", "lead", "architect", "senior", "head", "news"]
}

def compute_demographics_breakdown(db: Session) -> dict:
    posts = db.query(Post.author_bio, Post.language).all()
    total = len(posts) or 1
    
    age_counts = Counter({k: 0 for k in AGE_PROFILES})
    age_counts["Unclassified"] = 0

    geo_counts = Counter()
    geo_counts[UNCLASSIFIED_REGION] = 0

    lang_counts = Counter()

    for bio, lang in posts:
        lang_counts[lang or "en"] += 1
        if not bio:
            age_counts["Unclassified"] += 1
            geo_counts[UNCLASSIFIED_REGION] += 1
            continue
            
        bio_lower = bio.lower()
        
        # Age inference
        matched_age = False
        for segment, terms in AGE_PROFILES.items():
            if any(term in bio_lower for term in terms):
                age_counts[segment] += 1
                matched_age = True
                break
        if not matched_age:
            age_counts["Unclassified"] += 1
            
        # Geographic inference (shared gazetteer with the civic-risk map)
        matched_region = match_region_from_text(bio)
        geo_counts[matched_region or UNCLASSIFIED_REGION] += 1

    return {
        "age_distribution": {k: round((v / total) * 100, 1) for k, v in age_counts.items()},
        "geographic_distribution": {k: round((v / total) * 100, 1) for k, v in geo_counts.items()},
        "language_distribution": {k: round((v / total) * 100, 1) for k, v in lang_counts.items()}
    }