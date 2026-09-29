"""REST routes. All handlers are `async def` with no awaits, so each request
runs atomically on the event loop and the (non-thread-safe) cache needs no lock.

Route order matters: /cache/stats, /cache/config and /cache/clear are declared
before /cache/{key}. (A cache key literally named "stats" or "config" therefore
cannot be read via GET /cache/{key}.)
"""
from __future__ import annotations

from fastapi import APIRouter, Path, Request
from fastapi.responses import JSONResponse

from app.cache import CacheManager
from app.core.keys import candidate_keys
from app.schemas.cache_schema import (
    CacheClearResponse,
    CacheConfigResponse,
    CacheDeleteMissResponse,
    CacheDeleteResponse,
    CacheGetResponse,
    CacheMissResponse,
    CachePutRequest,
    CachePutResponse,
    CacheStatsResponse,
    HealthResponse,
    RootResponse,
    ValidationErrorResponse,
)

router = APIRouter()

KeyPath = Path(..., min_length=1, max_length=256, description="Cache key (int or string)")


def _manager(request: Request) -> CacheManager:
    return request.app.state.cache_manager


def _find_key(manager: CacheManager, raw: str):
    """Return the stored key matching a path segment, or None."""
    for candidate in candidate_keys(raw):
        if candidate in manager:  # does not touch stats/recency
            return candidate
    return None


@router.get("/", response_model=RootResponse, tags=["system"])
async def root():
    return {"service": "CachePulse Engine", "status": "running"}


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    return {"status": "healthy"}


@router.get("/cache/stats", response_model=CacheStatsResponse, tags=["cache"])
async def cache_stats(request: Request):
    s = _manager(request).stats()
    return {
        "hits": s["hits"],
        "misses": s["misses"],
        "hit_rate": round(s["hit_rate"], 2),
        "capacity": s["capacity"],
        "current_size": s["size"],
        "policy": s["policy"],
    }


@router.get("/cache/config", response_model=CacheConfigResponse, tags=["cache"])
async def cache_config(request: Request):
    m = _manager(request)
    return {"capacity": m.capacity, "policy": m.policy}


@router.post("/cache/clear", response_model=CacheClearResponse, tags=["cache"])
async def cache_clear(request: Request):
    removed = _manager(request).clear()
    return {
        "status": "cleared",
        "entries_removed": removed,
        "message": "All entries removed and statistics reset.",
    }


@router.put(
    "/cache",
    response_model=CachePutResponse,
    responses={422: {"model": ValidationErrorResponse}},
    tags=["cache"],
)
async def cache_put(payload: CachePutRequest, request: Request):
    """Insert or update an entry. Does not count as a hit or a miss."""
    manager = _manager(request)
    created = payload.key not in manager
    manager.put(payload.key, payload.value)
    return {"key": payload.key, "value": payload.value, "created": created}


@router.get(
    "/cache/{key}",
    response_model=CacheGetResponse,
    responses={404: {"model": CacheMissResponse}},
    tags=["cache"],
)
async def cache_get(request: Request, key: str = KeyPath):
    manager = _manager(request)
    found = _find_key(manager, key)
    if found is None:
        canonical = candidate_keys(key)[0]
        manager.get(canonical)  # records the miss
        body = CacheMissResponse(
            key=canonical,
            hit=False,
            error="key_not_found",
            message=f"Key {canonical!r} was not found in the cache.",
        )
        return JSONResponse(status_code=404, content=body.model_dump())
    value = manager.get(found)  # records the hit, updates recency/frequency
    return {"key": found, "value": value, "hit": True}


@router.delete(
    "/cache/{key}",
    response_model=CacheDeleteResponse,
    responses={404: {"model": CacheDeleteMissResponse}},
    tags=["cache"],
)
async def cache_delete(request: Request, key: str = KeyPath):
    manager = _manager(request)
    found = _find_key(manager, key)
    if found is None:
        canonical = candidate_keys(key)[0]
        body = CacheDeleteMissResponse(
            key=canonical,
            deleted=False,
            error="key_not_found",
            message=f"Key {canonical!r} was not found in the cache.",
        )
        return JSONResponse(status_code=404, content=body.model_dump())
    manager.delete(found)
    return {"key": found, "deleted": True, "message": f"Key {found!r} deleted."}