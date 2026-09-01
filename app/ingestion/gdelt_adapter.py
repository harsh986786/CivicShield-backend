"""
GDELT adapter -- real, live, geo-tagged news-coverage signals.

GDELT (gdeltproject.org) is a free, no-API-key global news monitoring
system that machine-geocodes news coverage in near-real-time. We use two
of its public endpoints:

1. GEO 2.0 API ("pointdata" mode) -- returns real lat/lon points where
   news coverage of our query terms was geographically anchored, updated
   every 15 minutes. This is what feeds the civic-unrest map layer.
   Docs: https://blog.gdeltproject.org/gdelt-geo-2-0-api-debuts/

2. DOC 2.0 API ("timelinetone" mode) -- returns the average sentiment
   ("tone") of news coverage matching our query over time, which we use
   as an independent, non-social-media negativity signal for the risk
   score.
   Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

This is a genuinely live external data source (not mocked), and it is
specifically well-suited to CivicShield's stated goal of an explainable
early-warning indicator: GDELT event coverage is a standard input used in
real academic/civic unrest-monitoring research (e.g. ICEWS-style systems).
"""
import re
import httpx

GEO_ENDPOINT = "https://api.gdeltproject.org/api/v2/geo/geo"
DOC_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"

# Keyword set used to focus GDELT on civic-unrest-relevant coverage.
# Kept broad but not alarmist -- these are standard event-monitoring terms,
# not targeting any group, ideology, or individual.
UNREST_KEYWORDS = [
    "protest", "riot", "curfew", "unrest", "clash", "communal violence",
    "mob violence", "police lathi charge", "internet shutdown", "strike",
    "bandh", "agitation",
]

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: str | None) -> str:
    if not html:
        return ""
    return _TAG_RE.sub(" ", html).strip()


class GDELTAdapter:
    """Fetches live, geo-tagged civic-unrest-relevant news signals for India."""

    def _build_unrest_query(self) -> str:
        keyword_block = " OR ".join(UNREST_KEYWORDS)
        return f"({keyword_block}) sourcecountry:india"

    async def fetch_unrest_geo_points(self, timespan: str = "24h", max_points: int = 250) -> list[dict]:
        """
        Returns real geo-tagged locations where India-focused unrest-related
        news coverage was concentrated, e.g.:
        [{"location_name": "...", "lat": .., "lon": .., "mention_count": .., "sample_headline": ".."}]
        """
        params = {
            "query": self._build_unrest_query(),
            "mode": "pointdata",
            "format": "geojson",
            "timespan": timespan,
            "maxpoints": str(max_points),
            "geores": "2",  # city/landmark-level precision only, no country-level noise
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(GEO_ENDPOINT, params=params)
                if resp.status_code != 200:
                    print(f"[GDELTAdapter] GEO API returned {resp.status_code}")
                    return []
                data = resp.json()
            except Exception as e:
                print(f"[GDELTAdapter] GEO API request failed: {e}")
                return []

        results = []
        for feature in data.get("features", []):
            props = feature.get("properties", {}) or {}
            geometry = feature.get("geometry", {}) or {}
            coords = geometry.get("coordinates")
            if not coords or len(coords) != 2:
                continue
            lon, lat = coords[0], coords[1]

            html_snippet = props.get("html", "")
            headline = _strip_html(html_snippet)[:200]

            results.append({
                "location_name": props.get("name", "Unknown"),
                "lat": float(lat),
                "lon": float(lon),
                "mention_count": int(props.get("count", 0) or 0),
                "sample_headline": headline,
            })
        return results

    async def fetch_unrest_tone(self, timespan: str = "24h") -> float | None:
        """
        Returns the average GDELT 'tone' score of India unrest-related coverage
        over the timespan (roughly: negative = more negative/alarming coverage,
        typical range -10..+10). Returns None if unavailable.
        """
        params = {
            "query": self._build_unrest_query(),
            "mode": "timelinetone",
            "format": "json",
            "timespan": timespan,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(DOC_ENDPOINT, params=params)
                if resp.status_code != 200:
                    print(f"[GDELTAdapter] DOC API returned {resp.status_code}")
                    return None
                data = resp.json()
            except Exception as e:
                print(f"[GDELTAdapter] DOC API request failed: {e}")
                return None

        try:
            timeline = data.get("timeline", [])
            if not timeline:
                return None
            series = timeline[0].get("data", [])
            if not series:
                return None
            values = [pt["value"] for pt in series if "value" in pt]
            return round(sum(values) / len(values), 2) if values else None
        except Exception as e:
            print(f"[GDELTAdapter] Failed to parse tone timeline: {e}")
            return None
