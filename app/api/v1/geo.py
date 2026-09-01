from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ingestion.gdelt_adapter import GDELTAdapter
from app.models.civic_event import CivicEvent
from app.services.geo_service import match_region_from_text, nearest_region, UNCLASSIFIED_REGION
from app.services.risk_service import compute_civic_risk_map

router = APIRouter(prefix="/geo", tags=["Geographic & Civic Risk"])


@router.post("/ingest-unrest-signals", summary="Pull live geo-tagged unrest signals from GDELT")
async def ingest_unrest_signals(timespan: str = "24h", db: Session = Depends(get_db)):
    """
    Fetches real, live, geo-coded India unrest-related news signals from
    GDELT (free public API, no key required) and stores them as CivicEvents.
    Intended to be run on a schedule (see app/workers) for continuous
    monitoring, but can also be triggered manually.
    """
    adapter = GDELTAdapter()
    points = await adapter.fetch_unrest_geo_points(timespan=timespan)
    avg_tone = await adapter.fetch_unrest_tone(timespan=timespan)

    stored = 0
    for point in points:
        region = match_region_from_text(point["location_name"]) or nearest_region(point["lat"], point["lon"])
        event = CivicEvent(
            source="gdelt",
            query_used="civic_unrest_india",
            location_name=point["location_name"],
            region=region,
            latitude=point["lat"],
            longitude=point["lon"],
            mention_count=point["mention_count"],
            avg_tone=avg_tone,
            sample_headline=point["sample_headline"],
        )
        db.add(event)
        stored += 1
    db.commit()

    return {
        "message": "GDELT unrest signal ingestion complete",
        "points_fetched": len(points),
        "events_stored": stored,
        "global_news_tone": avg_tone,
    }


@router.get("/civic-events", summary="Recent raw GDELT-sourced unrest events (map pins)")
def get_civic_events(limit: int = 100, db: Session = Depends(get_db)):
    events = (
        db.query(CivicEvent)
        .order_by(CivicEvent.fetched_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(events),
        "events": [
            {
                "location_name": e.location_name,
                "region": e.region,
                "lat": e.latitude,
                "lon": e.longitude,
                "mention_count": e.mention_count,
                "avg_tone": e.avg_tone,
                "sample_headline": e.sample_headline,
                "fetched_at": e.fetched_at,
            }
            for e in events
        ],
    }


@router.get("/risk-map", summary="Region-level explainable civic-risk scores (map-ready)")
def get_risk_map(unrest_lookback_hours: int = 48, db: Session = Depends(get_db)):
    """
    Fuses social-media sentiment/emotion (geo-tagged via author bio matching)
    with GDELT unrest-event density and news tone into a per-region,
    explainable risk score, ready to render as a choropleth/heat map.
    """
    return compute_civic_risk_map(db, unrest_lookback_hours=unrest_lookback_hours)
