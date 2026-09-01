from abc import ABC, abstractmethod
from app.schemas.social import NormalizedPost

class BaseSocialAdapter(ABC):
    @abstractmethod
    async def fetch_posts(self, query: str, limit: int = 50) -> list[NormalizedPost]:
        """Fetch and normalize social posts."""
        pass