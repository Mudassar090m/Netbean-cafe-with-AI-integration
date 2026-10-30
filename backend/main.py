"""FastAPI application factory for the Bright Bean Café backend."""
from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from backend.data import store
from backend.db.database import Base, engine
from backend.routers import contact, gallery, health, menu, orders, chat, recommend
from backend.seeds.gallery_seed import GALLERY_ITEMS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Resolve paths relative to this file so the server can be started from any
# working directory.
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).parent          # …/cafe/backend/
_CAFE_ROOT = _BACKEND_DIR.parent              # …/cafe/  ← static frontend root
_MENU_JSON = _CAFE_ROOT / "data" / "menu.json"


# ---------------------------------------------------------------------------
# Lifespan: startup tasks
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN001
    """Run startup tasks before the server begins accepting requests."""
    # 1. Seed in-memory stores (halts with SystemExit on bad menu.json)
    store.seed_menu(str(_MENU_JSON))
    store.seed_gallery(GALLERY_ITEMS)

    # 2. Create database tables (idempotent)
    Base.metadata.create_all(bind=engine)

    logger.info("Bright Bean API started — serving from %s", _CAFE_ROOT)
    yield
    # (shutdown logic would go here if needed)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Bright Bean Café API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # --- CORS middleware -------------------------------------------------
    default_origins = ["http://localhost", "http://127.0.0.1"]
    extra = os.getenv("ALLOWED_ORIGINS", "")
    extra_origins = [o.strip() for o in extra.split(",") if o.strip()]
    allowed_origins = default_origins + extra_origins

    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # --- Global exception handlers --------------------------------------

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Flatten Pydantic validation errors into a single detail string.
        Also catches malformed JSON bodies which FastAPI surfaces as a
        RequestValidationError with type 'json_invalid'.
        """
        errors = exc.errors()
        # If the only error is a JSON parse failure, return 400
        if len(errors) == 1 and errors[0].get("type") in (
            "json_invalid", "json_parse_error", "value_error.jsondecode"
        ):
            return JSONResponse(
                status_code=400,
                content={"detail": "Request body is not valid JSON"},
            )
        messages = []
        for error in errors:
            loc = " → ".join(str(l) for l in error["loc"] if l != "body")
            messages.append(f"{loc}: {error['msg']}" if loc else error["msg"])
        return JSONResponse(
            status_code=422,
            content={"detail": "; ".join(messages)},
        )

    @application.exception_handler(json.JSONDecodeError)
    async def json_decode_error_handler(
        request: Request, exc: json.JSONDecodeError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body is not valid JSON"},
        )

    @application.exception_handler(UnicodeDecodeError)
    async def unicode_decode_error_handler(
        request: Request, exc: UnicodeDecodeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Request body is not valid JSON"},
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all: log the full traceback but never expose it in the response."""
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # --- Routers --------------------------------------------------------
    # /api/* routes
    application.include_router(menu.router, prefix="/api")
    application.include_router(contact.router, prefix="/api")
    application.include_router(gallery.router, prefix="/api")
    application.include_router(orders.router, prefix="/api")
    application.include_router(chat.router, prefix="/api")
    application.include_router(recommend.router, prefix="/api")
    # /health (no prefix)
    application.include_router(health.router)

    # --- Static files ---------------------------------------------------
    # Must be mounted AFTER all API routes so /api/* always takes precedence.
    application.mount(
        "/",
        StaticFiles(directory=str(_CAFE_ROOT), html=True),
        name="static",
    )

    return application


app = create_app()
