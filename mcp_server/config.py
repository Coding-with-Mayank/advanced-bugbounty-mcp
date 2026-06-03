"""
Configuration — reads from .env file and environment variables.
All values have safe defaults so the server starts even without a .env.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Server ────────────────────────────────────────────────────────
    debug: bool = Field(False, env="DEBUG")
    log_file: str = Field("/app/logs/mcp_server.log", env="LOG_FILE")
    reports_dir: str = Field("/app/reports", env="REPORTS_DIR")
    screenshots_dir: str = Field("/app/screenshots", env="SCREENSHOTS_DIR")
    data_dir: str = Field("/app/data", env="DATA_DIR")

    # ── Scope & Safety ────────────────────────────────────────────────
    # Comma-separated list of allowed domains/IPs you have permission to test
    # Leave empty to allow all (your responsibility to test legally)
    allowed_scope: str = Field("", env="ALLOWED_SCOPE")

    # Always blocked — never scan these
    blocked_targets: str = Field(
        "localhost,127.0.0.1,0.0.0.0,169.254.169.254,10.0.0.0/8,192.168.0.0/16",
        env="BLOCKED_TARGETS",
    )

    # ── MongoDB ───────────────────────────────────────────────────────
    mongo_uri: str = Field(
        "mongodb://admin:changeme_please@mongodb:27017/bugbounty?authSource=admin",
        env="MONGO_URI",
    )
    mongo_password: str = Field("changeme_please", env="MONGO_PASSWORD")

    # ── Redis ─────────────────────────────────────────────────────────
    redis_url: str = Field("redis://:changeme_please@redis:6379/0", env="REDIS_URL")
    redis_password: str = Field("changeme_please", env="REDIS_PASSWORD")

    # ── Intelligence API keys (all optional) ──────────────────────────
    shodan_api_key: Optional[str] = Field(None, env="SHODAN_API_KEY")
    virustotal_api_key: Optional[str] = Field(None, env="VIRUSTOTAL_API_KEY")
    censys_api_id: Optional[str] = Field(None, env="CENSYS_API_ID")
    censys_api_secret: Optional[str] = Field(None, env="CENSYS_API_SECRET")
    securitytrails_api_key: Optional[str] = Field(None, env="SECURITYTRAILS_API_KEY")

    # ── Scanning defaults ─────────────────────────────────────────────
    default_threads: int = Field(50, env="DEFAULT_THREADS")
    default_timeout: int = Field(120, env="DEFAULT_TIMEOUT")
    rate_limit: int = Field(50, env="RATE_LIMIT")          # requests/sec for nuclei
    max_subdomains: int = Field(500, env="MAX_SUBDOMAINS")  # cap results

    # ── Notifications (optional) ──────────────────────────────────────
    slack_webhook: Optional[str] = Field(None, env="SLACK_WEBHOOK")
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")

    def ensure_dirs(self) -> None:
        """Create all required directories if they don't exist."""
        for d in [self.reports_dir, self.screenshots_dir, self.data_dir, Path(self.log_file).parent]:
            Path(d).mkdir(parents=True, exist_ok=True)

    @property
    def scope_list(self) -> list[str]:
        if not self.allowed_scope:
            return []
        return [s.strip() for s in self.allowed_scope.split(",") if s.strip()]

    @property
    def blocked_list(self) -> list[str]:
        return [s.strip() for s in self.blocked_targets.split(",") if s.strip()]


# Singleton used across the package
settings = Settings()
settings.ensure_dirs()
