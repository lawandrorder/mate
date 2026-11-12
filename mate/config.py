"""Environment configuration. Secrets are never hardcoded."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    host: str = "127.0.0.1"
    port: int = 8080
    data_dir: Path = Path("data")
    openrouter_api_key: str | None = None
    model: str = "openrouter/auto"
    http_referer: str = "https://mate.fm"
    app_title: str = "Mate"
    twilio_auth_token: str | None = None
    twilio_validate_signature: bool = False

    @property
    def openrouter_enabled(self) -> bool:
        return bool(self.openrouter_api_key)


def load_config(overrides: dict | None = None) -> Config:
    """Load config from the process environment, then optional overrides."""
    env = os.environ
    data_dir = Path(env.get("MATE_DATA_DIR", "data"))
    if not data_dir.is_absolute():
        data_dir = _repo_root() / data_dir
    cfg = Config(
        host=env.get("MATE_HOST", "127.0.0.1"),
        port=int(env.get("MATE_PORT", "8080")),
        data_dir=data_dir,
        openrouter_api_key=env.get("OPENROUTER_API_KEY") or None,
        model=env.get("MATE_MODEL", "openrouter/auto"),
        http_referer=env.get("MATE_HTTP_REFERER", "https://mate.fm"),
        app_title=env.get("MATE_APP_TITLE", "Mate"),
        twilio_auth_token=env.get("TWILIO_AUTH_TOKEN") or None,
        twilio_validate_signature=_truthy(env.get("TWILIO_VALIDATE_SIGNATURE", "0")),
    )
    if overrides:
        data = cfg.__dict__.copy()
        data.update({k: v for k, v in overrides.items() if v is not None})
        cfg = Config(**data)
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    return cfg


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
