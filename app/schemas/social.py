from datetime import datetime
from pydantic import BaseModel, Field

class NormalizedPost(BaseModel):
    platform: str
    platform_post_id: str
    author_id: str
    author_username: str | None = None
    author_bio: str | None = None
    text: str
    language: str = "en"
    created_at: datetime
    parent_post_id: str | None = None
    engagement_count: dict = Field(default_factory=lambda: {"likes": 0, "shares": 0, "comments": 0})
    raw_data: dict = Field(default_factory=dict)