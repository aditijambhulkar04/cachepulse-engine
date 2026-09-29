"""CachePulse Engine - FastAPI application.

Run:  uvicorn app.main:app --reload
Env:  CACHE_POLICY=LFU|LRU  CACHE_CAPACITY=50  CORS_ORIGINS=*
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.cache import CacheManager
from app.core.config import Settings, load_settings


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or load_settings()  # raises ConfigError on bad env values

    app = FastAPI(
        title="CachePulse Engine",
        description="In-memory LRU/LFU cache engine with O(1) operations.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.state.settings = settings
    app.state.cache_manager = CacheManager(settings.cache_policy, settings.cache_capacity)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,  # required to be False when origins is "*"
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [
            {"loc": [p for p in e["loc"]], "msg": str(e["msg"]), "type": str(e["type"])}
            for e in exc.errors()
        ]
        malformed_json = any(d["type"] == "json_invalid" for d in details)
        return JSONResponse(
            status_code=400 if malformed_json else 422,
            content={
                "error": "invalid_json" if malformed_json else "validation_error",
                "message": "Request body is not valid JSON."
                if malformed_json
                else "Request validation failed.",
                "details": details,
            },
        )

    app.include_router(router)
    return app


app = create_app()