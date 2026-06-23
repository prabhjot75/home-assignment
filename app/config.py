from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "BUSINESS_AI_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./bookmarks.db"

settings = Settings()