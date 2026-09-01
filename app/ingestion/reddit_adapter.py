import httpx
import xmltodict
from datetime import datetime, timezone
from app.schemas.social import NormalizedPost
from app.ingestion.base import BaseSocialAdapter

class RedditAdapter(BaseSocialAdapter):
    async def fetch_posts(self, query: str = "technology", limit: int = 25) -> list[NormalizedPost]:
        url = f"https://www.reddit.com/r/{query}/.rss?limit={limit}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=headers, timeout=12.0)
                if resp.status_code != 200:
                    print(f"[RedditAdapter] RSS Fetch failed with status {resp.status_code}")
                    return []
                feed_data = xmltodict.parse(resp.text)
            except Exception as e:
                print(f"[RedditAdapter] Request failed: {e}")
                return []
                
        entries = feed_data.get("feed", {}).get("entry", [])
        if isinstance(entries, dict):  # Single item returned
            entries = [entries]
            
        normalized = []
        for entry in entries[:limit]:
            post_id = entry.get("id", "").split("/")[-1]
            title = entry.get("title", "")
            author_obj = entry.get("author", {})
            author_name = author_obj.get("name", "/u/anonymous").replace("/u/", "")
            
            # Parse ISO timestamp
            updated_str = entry.get("updated", "")
            try:
                created_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
            except Exception:
                created_dt = datetime.now(timezone.utc)
                
            normalized.append(
                NormalizedPost(
                    platform="reddit",
                    platform_post_id=f"reddit_{post_id}",
                    author_id=f"usr_{author_name}",
                    author_username=author_name,
                    author_bio=f"Active contributor in r/{query}",
                    text=title,
                    language="en",
                    created_at=created_dt,
                    parent_post_id=None,
                    engagement_count={"likes": 0, "shares": 0, "comments": 0},
                    raw_data={"subreddit": query, "link": entry.get("link", {}).get("@href", "")}
                )
            )
        return normalized