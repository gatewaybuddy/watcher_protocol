"""Configuration management for Watcher Protocol."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Watcher Protocol"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database
    database_url: str = "postgresql+asyncpg://watcher:password@localhost:5432/watcher_db"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600  # 1 hour

    # Object Storage (MinIO/S3)
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "watcher-content"

    # AI/ML
    openai_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    classification_model: str = "distilbert-base-uncased"

    # Scrapers
    arxiv_api_url: str = "http://export.arxiv.org/api/query"
    arxiv_categories: List[str] = ["cs.AI", "cs.LG", "cs.CL", "cs.CY"]
    arxiv_scrape_interval_minutes: int = 60

    github_token: str = ""
    github_scrape_interval_minutes: int = 120

    rss_feeds: List[str] = [
        "https://www.alignmentforum.org/feed.xml",
        "https://www.lesswrong.com/feed.xml?view=community-rss&karmaThreshold=30"
    ]
    rss_scrape_interval_minutes: int = 30

    # Notifications
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "alerts@watcherprotocol.com"

    slack_webhook_url: str = ""
    discord_webhook_url: str = ""

    # Alerts
    enable_notifications: bool = True
    alert_batch_interval_minutes: int = 15
    max_alerts_per_batch: int = 50

    # Rate Limiting
    rate_limit_per_minute: int = 60
    scraper_rate_limit: int = 30

    # Monitoring
    enable_prometheus: bool = True
    enable_sentry: bool = False
    sentry_dsn: str = ""

    # Security
    api_keys: List[str] = []  # For API authentication
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
