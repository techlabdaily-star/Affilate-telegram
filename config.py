import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value or ""


def _parse_channels(raw: str) -> List[str]:
    if not raw:
        return []
    return [c.strip() for c in raw.split(",") if c.strip()]


@dataclass
class Settings:
    api_id: int
    api_hash: str
    string_session: str | None
    source_channels: List[str]
    target_channel: str
    extrape_username: str
    extrape_rate_limit_seconds: float
    trending_min_sources: int
    repost_enabled: bool
    repost_after_hours: int
    repost_trending_only: bool
    db_path: str = "deals.db"


def load_settings() -> Settings:
    api_id_raw = _get_env("TELEGRAM_API_ID", required=True)
    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise RuntimeError("TELEGRAM_API_ID must be an integer") from exc

    api_hash = _get_env("TELEGRAM_API_HASH", required=True)
    string_session = os.getenv("TELEGRAM_STRING_SESSION") or None

    source_channels = _parse_channels(os.getenv("SOURCE_CHANNELS", ""))
    if not source_channels:
        raise RuntimeError("SOURCE_CHANNELS must not be empty")

    target_channel = _get_env("TARGET_CHANNEL", required=True)

    extrape_username = os.getenv("EXTRAPE_USERNAME", "@ExtraPeBot")
    rate_limit_raw = os.getenv("EXTRAPE_RATE_LIMIT_SECONDS", "1.0")
    try:
        rate_limit = float(rate_limit_raw)
    except ValueError:
        rate_limit = 1.0

    trending_min_sources_raw = os.getenv("TRENDING_MIN_SOURCES", "3")
    try:
        trending_min_sources = int(trending_min_sources_raw)
    except ValueError:
        trending_min_sources = 3

    repost_enabled = os.getenv("REPOST_ENABLED", "false").lower() == "true"
    repost_after_hours_raw = os.getenv("REPOST_AFTER_HOURS", "8")
    try:
        repost_after_hours = int(repost_after_hours_raw)
    except ValueError:
        repost_after_hours = 8
    repost_trending_only = os.getenv("REPOST_TRENDING_ONLY", "true").lower() == "true"

    return Settings(
        api_id=api_id,
        api_hash=api_hash,
        string_session=string_session,
        source_channels=source_channels,
        target_channel=target_channel,
        extrape_username=extrape_username,
        extrape_rate_limit_seconds=rate_limit,
        trending_min_sources=trending_min_sources,
        repost_enabled=repost_enabled,
        repost_after_hours=repost_after_hours,
        repost_trending_only=repost_trending_only,
    )

