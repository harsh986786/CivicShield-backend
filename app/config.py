from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH Social Media Intelligence"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sih_db"
    API_V1_STR: str = "/api/v1"
    # Comma-separated list of allowed frontend origins, e.g.
    # "https://civicshield.vercel.app,http://localhost:5173"
    # Defaults to "*" (open) for easy local/hackathon dev; set this explicitly
    # once you have a deployed frontend URL.
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()