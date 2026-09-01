import os
import re

SENSATIONAL_PHRASES = [
    "you won't believe", "share before it's deleted", "share before deleted",
    "mainstream media won't tell you", "media is hiding", "wake up india",
    "forward this to everyone", "forward to all your contacts",
    "shocking truth", "they don't want you to know", "government is hiding",
    "must watch before deleted", "breaking:", "urgent:", "alert:",
    "100% true", "proof inside", "banned video", "leaked video"
]

SOURCE_ATTRIBUTION_MARKERS = [
    "according to", "reported by", "source:", "via ", "http://", "https://",
    "confirmed by", "official statement"
]

def _sensationalism_score(text: str) -> tuple[float, dict]:
    lower = text.lower()
    length = max(len(text), 1)

    # 1. Sensational phrase hits
    phrase_hits = sum(1 for p in SENSATIONAL_PHRASES if p in lower)
    phrase_score = min(phrase_hits * 25, 50)

    # 2. ALL-CAPS ratio
    letters = [c for c in text if c.isalpha()]
    caps_ratio = (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0
    caps_score = min(caps_ratio * 100, 25)

    # 3. Exclamation punctuation density
    exclaim_density = text.count("!") / (length / 100)
    exclaim_score = min(exclaim_density * 5, 15)

    # 4. Missing source attribution
    has_attribution = any(marker in lower for marker in SOURCE_ATTRIBUTION_MARKERS)
    no_source_score = 0 if has_attribution else 10

    total = round(min(phrase_score + caps_score + exclaim_score + no_source_score, 100), 1)
    return total, {
        "sensational_phrase_hits": phrase_hits,
        "caps_ratio_pct": round(caps_ratio * 100, 1),
        "exclaim_density_per_100_chars": round(exclaim_density, 2)
    }

def _risk_level(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Elevated"
    if score >= 25:
        return "Moderate"
    return "Low"

def analyze_credibility(text: str) -> dict:
    if not text or not text.strip():
        return {
            "misinformation_risk_score": 0.0,
            "risk_level": "Low",
            "sensationalism_score": 0.0,
            "model_fake_probability": None,
            "contributing_factors": {},
            "model_version": "credibility-heuristic-v1.0"
        }

    sens_score, sens_factors = _sensationalism_score(text)
    
    # Heuristic probability calculation (replaces heavy HuggingFace model)
    fake_prob = round(sens_score / 100.0, 3)
    combined = sens_score

    return {
        "misinformation_risk_score": combined,
        "risk_level": _risk_level(combined),
        "sensationalism_score": sens_score,
        "model_fake_probability": fake_prob,
        "contributing_factors": sens_factors,
        "model_version": "credibility-heuristic-v1.0"
    }