from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from typing import cast

from app.core.database import get_db
from app.models.post import Post
from app.ingestion.mock_adapter import generate_mock_posts
from app.ingestion.reddit_adapter import RedditAdapter
from app.ingestion.telegram_adapter import TelegramAdapter
from app.ingestion.x_adapter import XAdapter

# 1. Initialize the Router First
router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])

# 2. Mock Ingestion Endpoint
@router.post("/mock", summary="Generate & insert mock social media posts")
def ingest_mock_data(count: int = 30, db: Session = Depends(get_db)):
    mock_posts = generate_mock_posts(count=count)
    inserted_count = 0

    for item in mock_posts:
        stmt = insert(Post).values(
            platform=item.platform,
            platform_post_id=item.platform_post_id,
            author_id=item.author_id,
            author_username=item.author_username,
            author_bio=item.author_bio,
            text=item.text,
            language=item.language,
            created_at=item.created_at,
            parent_post_id=item.parent_post_id,
            engagement_count=item.engagement_count,
            raw_data=item.raw_data,
            is_processed=False
        ).on_conflict_do_nothing(
            index_elements=["platform", "platform_post_id"]
        )
        result = db.execute(stmt)
        inserted_count += cast(CursorResult, result).rowcount

    db.commit()
    return {"status": "success", "generated": len(mock_posts), "inserted_new_records": inserted_count}

# 3. Live Reddit Ingestion Endpoint
@router.post("/reddit", summary="Fetch real-time posts from a public Subreddit")
async def ingest_reddit_data(subreddit: str = "technology", limit: int = 15, db: Session = Depends(get_db)):
    adapter = RedditAdapter()
    reddit_posts = await adapter.fetch_posts(query=subreddit, limit=limit)
    inserted_count = 0

    for item in reddit_posts:
        stmt = insert(Post).values(
            platform=item.platform,
            platform_post_id=item.platform_post_id,
            author_id=item.author_id,
            author_username=item.author_username,
            author_bio=item.author_bio,
            text=item.text,
            language=item.language,
            created_at=item.created_at,
            parent_post_id=item.parent_post_id,
            engagement_count=item.engagement_count,
            raw_data=item.raw_data,
            is_processed=False
        ).on_conflict_do_nothing(
            index_elements=["platform", "platform_post_id"]
        )
        result = db.execute(stmt)
        inserted_count += cast(CursorResult, result).rowcount

    db.commit()
    return {"status": "success", "fetched": len(reddit_posts), "inserted_new_records": inserted_count}

# 4. Live Telegram Ingestion Endpoint
@router.post("/telegram", summary="Fetch real-time messages from a public Telegram channel")
async def ingest_telegram_data(channel: str = "durov", limit: int = 15, db: Session = Depends(get_db)):
    adapter = TelegramAdapter()
    tg_posts = await adapter.fetch_posts(query=channel, limit=limit)
    inserted_count = 0

    for item in tg_posts:
        stmt = insert(Post).values(
            platform=item.platform,
            platform_post_id=item.platform_post_id,
            author_id=item.author_id,
            author_username=item.author_username,
            author_bio=item.author_bio,
            text=item.text,
            language=item.language,
            created_at=item.created_at,
            parent_post_id=item.parent_post_id,
            engagement_count=item.engagement_count,
            raw_data=item.raw_data,
            is_processed=False
        ).on_conflict_do_nothing(
            index_elements=["platform", "platform_post_id"]
        )
        result = db.execute(stmt)
        inserted_count += cast(CursorResult, result).rowcount

    db.commit()
    return {"status": "success", "fetched": len(tg_posts), "inserted_new_records": inserted_count}

# 5. Parallel Batch Live Ingestion Endpoint
@router.post("/batch-live", summary="Fetch live data across multiple subreddits and Telegram channels simultaneously")
async def ingest_batch_live(db: Session = Depends(get_db)):
    reddit_adapter = RedditAdapter()
    telegram_adapter = TelegramAdapter()
    
    subreddits = ["technology", "artificial", "MachineLearning"]
    channels = ["techcrunch", "durov", "telegram"]
    
    all_posts = []
    
    for sub in subreddits:
        posts = await reddit_adapter.fetch_posts(query=sub, limit=10)
        all_posts.extend(posts)
        
    for ch in channels:
        posts = await telegram_adapter.fetch_posts(query=ch, limit=10)
        all_posts.extend(posts)
        
    inserted_count = 0
    for item in all_posts:
        stmt = insert(Post).values(
            platform=item.platform,
            platform_post_id=item.platform_post_id,
            author_id=item.author_id,
            author_username=item.author_username,
            author_bio=item.author_bio,
            text=item.text,
            language=item.language,
            created_at=item.created_at,
            parent_post_id=item.parent_post_id,
            engagement_count=item.engagement_count,
            raw_data=item.raw_data,
            is_processed=False
        ).on_conflict_do_nothing(
            index_elements=["platform", "platform_post_id"]
        )
        res = db.execute(stmt)
        inserted_count += cast(CursorResult, res).rowcount
        
    db.commit()
    return {
        "status": "success",
        "total_sources_queried": len(subreddits) + len(channels),
        "total_fetched": len(all_posts),
        "newly_inserted": inserted_count
    }

@router.post("/x", summary="Fetch/stimulate real time posts from X (Twitter)")
async def ingest_x_data(query: str = "technology", limit: int = 15, db: Session = Depends(get_db)):
    adapter = XAdapter()
    x_posts = await adapter.fetch_posts(query=query, limit=limit)
    inserted_count = 0

    for item in x_posts:
        stmt = insert(Post).values(
            platform=item.platform,
            platform_post_id=item.platform_post_id,
            author_id=item.author_id,
            author_username=item.author_username,
            author_bio=item.author_bio,
            text=item.text,
            language=item.language,
            created_at=item.created_at,
            parent_post_id=item.parent_post_id,
            engagement_count=item.engagement_count,
            raw_data=item.raw_data,
            is_processed=False
        ).on_conflict_do_nothing(
            index_elements=["platform", "platform_post_id"]
        )
        res = db.execute(stmt)
        inserted_count += cast(CursorResult, res).rowcount

    db.commit()
    return {"status": "success", "fetched": len(x_posts), "inserted_new_records": inserted_count}
        