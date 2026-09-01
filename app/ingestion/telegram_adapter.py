import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.schemas.social import NormalizedPost
from app.ingestion.base import BaseSocialAdapter

class TelegramAdapter(BaseSocialAdapter):
    async def fetch_posts(self, query: str = "durov", limit: int = 20) -> list[NormalizedPost]:
        channel_name = query.replace("@", "").strip()
        url = f"https://t.me/s/{channel_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=headers, timeout=12.0)
                if resp.status_code != 200:
                    print(f"[TelegramAdapter] Fetch failed with status {resp.status_code}")
                    return []
                html = resp.text
            except Exception as e:
                print(f"[TelegramAdapter] Request error: {e}")
                return []
                
        soup = BeautifulSoup(html, "html.parser")
        # Grab post wrap containers
        message_elements = soup.find_all("div", class_="tgme_widget_message_wrap")
        
        normalized = []
        for wrap in message_elements[-limit:]:
            msg = wrap.find("div", class_="tgme_widget_message")
            if not msg:
                continue
                
            text_elem = msg.find("div", class_="tgme_widget_message_text")
            if not text_elem:
                continue
            text = text_elem.get_text(separator=" ").strip()
            
            data_post = msg.get("data-post", f"{channel_name}/0")
            post_id = data_post.split("/")[-1]
            
            time_elem = msg.find("time")
            if time_elem and time_elem.get("datetime"):
                dt_str = time_elem.get("datetime")
                try:
                    created_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                except Exception:
                    created_dt = datetime.now(timezone.utc)
            else:
                created_dt = datetime.now(timezone.utc)
                
            normalized.append(
                NormalizedPost(
                    platform="telegram",
                    platform_post_id=f"tg_{channel_name}_{post_id}",
                    author_id=f"usr_tg_{channel_name}",
                    author_username=channel_name,
                    author_bio=f"Official Telegram Broadcast Channel @{channel_name}",
                    text=text,
                    language="en",
                    created_at=created_dt,
                    parent_post_id=None,
                    engagement_count={"likes": 0, "shares": 0, "comments": 0},
                    raw_data={"channel": channel_name, "message_id": post_id}
                )
            )
        return normalized