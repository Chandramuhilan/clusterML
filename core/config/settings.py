"""ClusterML Configuration Settings.

Centralized settings loaded from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration loaded from environment."""

    # Master
    master_host: str = Field(default="0.0.0.0")
    master_port: int = Field(default=8080)
    api_prefix: str = Field(default="/api/v1")

    # Scheduler
    scheduler_interval_seconds: float = Field(default=5.0, description="How often the scheduler runs")
    node_timeout_seconds: float = Field(default=90.0, description="Mark node offline after this many seconds without heartbeat")
    max_concurrent_jobs_per_node: int = Field(default=2)

    # Auth
    api_key: Optional[str] = Field(default=None, description="API key for authentication (None = open access)")

    # Storage
    storage_backend: str = Field(default="memory", description="'memory' for dev, 'sqlite' or 'postgres' for prod")
    database_url: Optional[str] = None

    # Logging
    log_level: str = Field(default="INFO")
    dev_mode: bool = Field(default=False)

    # CORS
    cors_origins: str = Field(default="*")


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance, reading from environment."""
    return Settings(
        master_host=os.getenv("MASTER_HOST", "0.0.0.0"),
        master_port=int(os.getenv("MASTER_PORT", "8080")),
        api_key=os.getenv("API_KEY"),
        storage_backend=os.getenv("STORAGE_BACKEND", "memory"),
        database_url=os.getenv("DATABASE_URL"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        dev_mode=os.getenv("DEV_MODE", "false").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "*"),
        scheduler_interval_seconds=float(os.getenv("SCHEDULER_INTERVAL", "5.0")),
        node_timeout_seconds=float(os.getenv("NODE_TIMEOUT", "90.0")),
        max_concurrent_jobs_per_node=int(os.getenv("MAX_CONCURRENT_JOBS", "2")),
    )
