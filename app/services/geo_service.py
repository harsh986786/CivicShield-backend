"""
Canonical India geography reference for CivicShield.

This is the single source of truth for mapping free-text (bios, post text,
GDELT location names) onto a consistent set of Indian states/UTs, each with
a centroid lat/lon so results can be plotted on a map and so different
signals (social posts, GDELT unrest events) can be aggregated onto the same
geographic buckets.

NOTE: These are coarse state-level centroids for aggregate visualization,
not precise geocoding. This is intentional -- CivicShield reasons about
aggregate public-signal patterns, not individual-level location tracking.
"""
from math import radians, sin, cos, sqrt, atan2

# state/UT -> (centroid_lat, centroid_lon, [keywords/cities used for text matching])
INDIA_REGIONS: dict[str, dict] = {
    "Delhi NCR":        {"lat": 28.6139, "lon": 77.2090, "keywords": ["delhi", "new delhi", "noida", "gurgaon", "gurugram", "ncr", "faridabad", "ghaziabad"]},
    "Uttar Pradesh":     {"lat": 26.8467, "lon": 80.9462, "keywords": ["lucknow", "kanpur", "varanasi", "prayagraj", "allahabad", "agra", "meerut", "uttar pradesh", " up "]},
    "Punjab":            {"lat": 31.1471, "lon": 75.3412, "keywords": ["punjab", "chandigarh", "amritsar", "ludhiana", "jalandhar"]},
    "Haryana":           {"lat": 29.0588, "lon": 76.0856, "keywords": ["haryana", "hisar", "rohtak", "panipat"]},
    "Rajasthan":         {"lat": 27.0238, "lon": 74.2179, "keywords": ["rajasthan", "jaipur", "jodhpur", "udaipur", "kota", "ajmer"]},
    "Bihar":             {"lat": 25.0961, "lon": 85.3131, "keywords": ["bihar", "patna", "gaya", "muzaffarpur", "bhagalpur"]},
    "Jharkhand":         {"lat": 23.6102, "lon": 85.2799, "keywords": ["jharkhand", "ranchi", "jamshedpur", "dhanbad"]},
    "West Bengal":       {"lat": 22.9868, "lon": 87.8550, "keywords": ["west bengal", "kolkata", "howrah", "siliguri", "durgapur"]},
    "Odisha":            {"lat": 20.9517, "lon": 85.0985, "keywords": ["odisha", "orissa", "bhubaneswar", "cuttack", "rourkela"]},
    "Assam / Northeast": {"lat": 26.2006, "lon": 92.9376, "keywords": ["assam", "guwahati", "manipur", "meghalaya", "nagaland", "tripura", "mizoram", "sikkim", "arunachal"]},
    "Maharashtra":       {"lat": 19.7515, "lon": 75.7139, "keywords": ["maharashtra", "mumbai", "pune", "nagpur", "nashik", "thane", "aurangabad"]},
    "Gujarat":           {"lat": 22.2587, "lon": 71.1924, "keywords": ["gujarat", "ahmedabad", "surat", "vadodara", "rajkot"]},
    "Madhya Pradesh":    {"lat": 22.9734, "lon": 78.6569, "keywords": ["madhya pradesh", " mp ", "bhopal", "indore", "gwalior", "jabalpur"]},
    "Chhattisgarh":      {"lat": 21.2787, "lon": 81.8661, "keywords": ["chhattisgarh", "raipur", "bilaspur", "bastar"]},
    "Karnataka":         {"lat": 15.3173, "lon": 75.7139, "keywords": ["karnataka", "bengaluru", "bangalore", "mysuru", "mysore", "mangalore", "hubli"]},
    "Telangana":         {"lat": 18.1124, "lon": 79.0193, "keywords": ["telangana", "hyderabad", "warangal", "nizamabad"]},
    "Andhra Pradesh":    {"lat": 15.9129, "lon": 79.7400, "keywords": ["andhra pradesh", "vijayawada", "visakhapatnam", "vizag", "tirupati"]},
    "Tamil Nadu":        {"lat": 11.1271, "lon": 78.6569, "keywords": ["tamil nadu", "chennai", "coimbatore", "madurai", "trichy", "salem"]},
    "Kerala":            {"lat": 10.8505, "lon": 76.2711, "keywords": ["kerala", "kochi", "cochin", "thiruvananthapuram", "kozhikode", "calicut"]},
    "Jammu & Kashmir":   {"lat": 33.7782, "lon": 76.5762, "keywords": ["jammu", "kashmir", "srinagar", "j&k", "leh", "ladakh"]},
    "International":     {"lat": 20.0, "lon": 0.0, "keywords": ["usa", "uk", "california", "london", "canada", "germany", "singapore", "dubai", "australia"]},
}

UNCLASSIFIED_REGION = "Other / Undefined"


def match_region_from_text(text: str | None) -> str | None:
    """Match free text (bio, post body, GDELT location name) to a region key."""
    if not text:
        return None
    lower = f" {text.lower()} "
    for region, meta in INDIA_REGIONS.items():
        if any(kw in lower for kw in meta["keywords"]):
            return region
    return None


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def nearest_region(lat: float, lon: float) -> str:
    """Snap an arbitrary lat/lon (e.g. from GDELT) to the nearest known region centroid."""
    best_region, best_dist = UNCLASSIFIED_REGION, float("inf")
    for region, meta in INDIA_REGIONS.items():
        if region == "International":
            continue
        d = _haversine_km(lat, lon, meta["lat"], meta["lon"])
        if d < best_dist:
            best_region, best_dist = region, d
    # If it's genuinely far from every Indian centroid, don't force-fit it
    if best_dist > 800:
        return UNCLASSIFIED_REGION
    return best_region


def region_centroid(region: str) -> tuple[float, float] | None:
    meta = INDIA_REGIONS.get(region)
    return (meta["lat"], meta["lon"]) if meta else None
