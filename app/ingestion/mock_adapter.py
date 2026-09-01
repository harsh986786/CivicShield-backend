import random
from datetime import datetime, timedelta, timezone
from app.schemas.social import NormalizedPost

SAMPLE_USERS = [
    {"id": "usr_tech_guru", "username": "tech_guru", "bio": "Senior Software Engineer | Tech Lead"},
    {"id": "usr_student_dan", "username": "dan_student", "bio": "Computer Science undergrad | Student @ IIT"},
    {"id": "usr_news_hub", "username": "daily_news_hub", "bio": "Official News Aggregator | 24/7 Updates"},
    {"id": "usr_dev_sam", "username": "sam_builds", "bio": "Fullstack Dev & Open Source Contributor"},
    {"id": "usr_finance_pro", "username": "crypto_macro", "bio": "Financial Analyst & Market Researcher"}
]

SAMPLE_TEXTS = [
    "Loving the new AI governance guidelines! Major step forward. #TechPolicy #AI",
    "Completely unacceptable server outage today. Terrible reliability. #TechOutage #Angry",
    "Is anyone else noticing performance drops on platform updates? #TechPolicy",
    "Great collaborative session with @tech_guru discussing data pipelines! #AI",
    "Discussions around #CyberSecPolicy are escalating fast across channels.",
    "Student community hackathons are reaching record attendance this season! #StudentsInTech"
]

def generate_mock_posts(count: int = 50) -> list[NormalizedPost]:
    posts = []
    base_time = datetime.now(timezone.utc) - timedelta(hours=6)

    for i in range(count):
        user = random.choice(SAMPLE_USERS)
        created_at = base_time + timedelta(minutes=i * 6)
        text = random.choice(SAMPLE_TEXTS)
        platform = random.choice(["x", "telegram", "reddit"])
        
        # Link simulation: some posts reference earlier authors
        parent_post_id = f"mock_{i-1}" if (i > 0 and random.random() > 0.6) else None

        post = NormalizedPost(
            platform=platform,
            platform_post_id=f"post_{platform}_{i}_{int(created_at.timestamp())}",
            author_id=user["id"],
            author_username=user["username"],
            author_bio=user["bio"],
            text=text,
            language="en",
            created_at=created_at,
            parent_post_id=parent_post_id,
            engagement_count={
                "likes": random.randint(0, 300),
                "shares": random.randint(0, 80),
                "comments": random.randint(0, 45)
            },
            raw_data={"source": "mock_generator", "simulated": True}
        )
        posts.append(post)

    return posts