"""API routes for admin operations."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ScraperStatusResponse(BaseModel):
    """Response model for scraper status."""
    scraper_name: str
    enabled: bool
    last_run_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_error_at: Optional[datetime]
    last_error_message: Optional[str]
    total_runs: int
    successful_runs: int
    failed_runs: int
    items_collected: int
    success_rate: float

    class Config:
        from_attributes = True


class SystemHealth(BaseModel):
    """System health status."""
    status: str  # healthy, degraded, unhealthy
    database: str  # connected, disconnected
    redis: str  # connected, disconnected
    scrapers_running: int
    scrapers_failed: int
    disk_usage_percent: float
    memory_usage_percent: float


@router.get("/health", response_model=SystemHealth)
async def system_health():
    """
    Get comprehensive system health status.

    Checks database, Redis, scrapers, and system resources.
    """
    # TODO: Implement health checks
    return SystemHealth(
        status="healthy",
        database="connected",
        redis="connected",
        scrapers_running=0,
        scrapers_failed=0,
        disk_usage_percent=0.0,
        memory_usage_percent=0.0
    )


@router.get("/scrapers/status", response_model=List[ScraperStatusResponse])
async def get_scrapers_status():
    """
    Get status of all scrapers.

    Shows execution history, success rates, and current state.
    """
    # TODO: Query scraper_status table
    return []


@router.post("/scrapers/{scraper_name}/trigger")
async def trigger_scraper(scraper_name: str):
    """
    Manually trigger a scraper to run immediately.

    Useful for testing or forcing an immediate update.
    """
    # TODO: Implement scraper triggering
    # Validate scraper name
    valid_scrapers = ["arxiv", "alignment_forum", "github", "rss"]
    if scraper_name not in valid_scrapers:
        raise HTTPException(
            status_code=404,
            detail=f"Scraper '{scraper_name}' not found. Valid scrapers: {valid_scrapers}"
        )

    # Trigger scraper
    return {
        "status": "triggered",
        "scraper": scraper_name,
        "triggered_at": datetime.utcnow()
    }


@router.post("/scrapers/{scraper_name}/enable")
async def enable_scraper(scraper_name: str):
    """
    Enable a scraper.
    """
    # TODO: Update scraper_status table
    return {"status": "enabled", "scraper": scraper_name}


@router.post("/scrapers/{scraper_name}/disable")
async def disable_scraper(scraper_name: str):
    """
    Disable a scraper.
    """
    # TODO: Update scraper_status table
    return {"status": "disabled", "scraper": scraper_name}


class DatabaseStats(BaseModel):
    """Database statistics."""
    total_items: int
    total_topics: int
    total_alerts: int
    total_subscriptions: int
    database_size_mb: float
    largest_tables: List[dict]


@router.get("/database/stats", response_model=DatabaseStats)
async def get_database_stats():
    """
    Get database statistics and table sizes.
    """
    # TODO: Query database metadata
    return DatabaseStats(
        total_items=0,
        total_topics=0,
        total_alerts=0,
        total_subscriptions=0,
        database_size_mb=0.0,
        largest_tables=[]
    )


@router.post("/database/cleanup")
async def cleanup_database(
    days_old: int = 365
):
    """
    Clean up old data from the database.

    Removes items older than the specified number of days.
    """
    # TODO: Implement cleanup logic with safety checks
    return {
        "status": "cleanup_scheduled",
        "days_old": days_old,
        "estimated_items": 0
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear Redis cache.
    """
    # TODO: Implement cache clearing
    return {"status": "cache_cleared", "cleared_at": datetime.utcnow()}


class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: datetime
    level: str
    logger: str
    message: str


@router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    level: str = "INFO",
    limit: int = 100
):
    """
    Get recent application logs.

    Filter by log level and limit number of entries.
    """
    # TODO: Implement log retrieval (requires log aggregation)
    return []
