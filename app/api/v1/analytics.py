from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.workers.pipeline_worker import run_analytics_pipeline

router = APIRouter(prefix="/analytics", tags=["Analytics & Pipeline"])

def background_pipeline_job():
    db = SessionLocal()
    try:
        run_analytics_pipeline(db)
    finally:
        db.close()

@router.post("/run-pipeline", summary="Trigger NLP & Graph processing")
def trigger_pipeline(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    result = run_analytics_pipeline(db)
    return {"message": "Pipeline execution finished", "result": result}