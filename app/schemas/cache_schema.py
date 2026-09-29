"""Pydantic request/response models."""
from __future__ import annotations

from typing import Annotated, Any, List, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, StringConstraints, field_validator

# int or non-empty string (max 256 chars). Booleans are rejected.
CacheKey = Union[
    StrictInt,
    Annotated[StrictStr, StringConstraints(min_length=1, max_length=256)],
]

MAX_STRING_VALUE_LENGTH = 1_000_000


class CachePutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: CacheKey
    value: Any = Field(..., description="Any non-null JSON value")

    @field_validator("value")
    @classmethod
    def value_not_null(cls, v: Any) -> Any:
        if v is None:
            raise ValueError("value must not be null")
        if isinstance(v, str) and len(v) > MAX_STRING_VALUE_LENGTH:
            raise ValueError(f"string value too long (max {MAX_STRING_VALUE_LENGTH} chars)")
        return v


class CachePutResponse(BaseModel):
    key: CacheKey
    value: Any
    created: bool = Field(..., description="True if a new entry was created, False if updated")


class CacheGetResponse(BaseModel):
    key: CacheKey
    value: Any
    hit: bool = True


class CacheMissResponse(BaseModel):
    key: CacheKey
    hit: bool = False
    error: str = "key_not_found"
    message: str


class CacheDeleteResponse(BaseModel):
    key: CacheKey
    deleted: bool = True
    message: str


class CacheDeleteMissResponse(BaseModel):
    key: CacheKey
    deleted: bool = False
    error: str = "key_not_found"
    message: str


class CacheStatsResponse(BaseModel):
    hits: int
    misses: int
    hit_rate: float
    capacity: int
    current_size: int
    policy: str


class CacheConfigResponse(BaseModel):
    capacity: int
    policy: str


class CacheClearResponse(BaseModel):
    status: str = "cleared"
    entries_removed: int
    message: str


class RootResponse(BaseModel):
    service: str
    status: str


class HealthResponse(BaseModel):
    status: str


class ErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    error: str = "validation_error"
    message: str
    details: List[ErrorDetail]