"""Application settings, read from environment variables.

CACHE_POLICY    LRU | LFU   (default LFU)
CACHE_CAPACITY  1..1_000_000 (default 50)
CORS_ORIGINS    comma-separated origins, or "*" (default "*")
"""
from __future__ import annotations

import os
from typing import List, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

DEFAULT_POLICY = "LFU"
DEFAULT_CAPACITY = 50
MAX_CAPACITY = 1_000_000
VALID_POLICIES = ("LRU", "LFU")


class ConfigError(ValueError):
    """Raised when environment configuration is invalid."""


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache_policy: str = DEFAULT_POLICY
    cache_capacity: int = Field(default=DEFAULT_CAPACITY, ge=1, le=MAX_CAPACITY)
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    @field_validator("cache_policy", mode="before")
    @classmethod
    def normalize_policy(cls, v):
        if not isinstance(v, str):
            raise ValueError("cache_policy must be a string: LRU or LFU")
        v = v.strip().upper()
        if v not in VALID_POLICIES:
            raise ValueError(f"cache_policy must be one of {list(VALID_POLICIES)}, got {v!r}")
        return v


def load_settings(env: Optional[Mapping[str, str]] = None) -> Settings:
    """Build Settings from environment variables (or a supplied mapping)."""
    env = os.environ if env is None else env
    raw: dict = {}
    if env.get("CACHE_POLICY", "").strip():
        raw["cache_policy"] = env["CACHE_POLICY"]
    if env.get("CACHE_CAPACITY", "").strip():
        raw["cache_capacity"] = env["CACHE_CAPACITY"].strip()
    if env.get("CORS_ORIGINS", "").strip():
        raw["cors_origins"] = [o.strip() for o in env["CORS_ORIGINS"].split(",") if o.strip()]
    try:
        return Settings(**raw)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
        )
        raise ConfigError(f"Invalid CachePulse configuration ({problems})") from exc