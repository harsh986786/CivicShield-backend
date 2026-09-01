from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.timeline import router as timeline_router
from app.api.v1.network import router as network_router
from app.api.v1.geo import router as geo_router
from app.api.v1.credibility import router as credibility_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

_origins = ["*"] if settings.CORS_ORIGINS.strip() == "*" else [
    o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    # Wildcard origins + credentials is rejected by browsers per the CORS
    # spec anyway, so only allow credentials once specific origins are set.
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(timeline_router, prefix=settings.API_V1_STR)
app.include_router(network_router, prefix=settings.API_V1_STR)
app.include_router(geo_router, prefix=settings.API_V1_STR)
app.include_router(credibility_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}