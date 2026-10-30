# Implementation Plan: FastAPI Backend for Bright Bean Café

## Overview

Implement a FastAPI backend in `backend/` that replaces the static `data/menu.json` fetch with a REST API, persists contact form submissions in SQLite, and serves gallery metadata dynamically. The backend coexists with the existing static frontend via a `StaticFiles` mount. All 10 correctness properties from the design are covered by Hypothesis property-based tests and pytest integration tests.

---

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create `backend/` directory layout: `routers/`, `models/`, `data/`, `db/`, `seeds/`, `tests/`
  - Write `backend/requirements.txt` pinning `fastapi`, `uvicorn[standard]`, `pydantic[email]`, `sqlalchemy`, `pytest`, `httpx`, `hypothesis`
  - Create `backend/__init__.py`, `backend/routers/__init__.py`, `backend/models/__init__.py`, `backend/data/__init__.py`, `backend/db/__init__.py`, `backend/seeds/__init__.py`, `backend/tests/__init__.py`
  - _Requirements: 8.1_

- [ ] 2. Define Pydantic models
  - [ ] 2.1 Create `backend/models/menu.py` with `MenuItem` Pydantic v2 model
    - Fields: `id` (positive int), `name` (1–100 chars), `category` (1–50 chars), `description` (0–500 chars), `price` (0.01–9999.99), `image` (non-empty, max 2048 chars), `featured` (bool, optional), `tags` (list[str], optional, max 20 items each ≤50 chars)
    - `model_config = ConfigDict(from_attributes=True)`
    - _Requirements: 1.5_

  - [ ] 2.2 Create `backend/models/gallery.py` with `GalleryItem` Pydantic v2 model
    - Fields: `id` (positive int), `category` (non-empty str), `image` (non-empty str), `label` (non-empty str)
    - _Requirements: 4.5_

  - [ ] 2.3 Create `backend/models/contact.py` with `ContactMessage`, `ContactMessageResponse`, `ErrorResponse`, and `HealthResponse` Pydantic v2 models
    - `ContactMessage`: `name` (min 2 non-whitespace, max 100), `email` (EmailStr, max 254), `subject` (min 2 non-whitespace, max 150), `message` (min 6 non-whitespace, max 2000); `@field_validator` on `name`, `subject`, `message` to reject whitespace-only values
    - `ContactMessageResponse`: `id`, `name`, `email`, `subject`, `message`, `submitted_at`; `model_config = ConfigDict(from_attributes=True)`
    - `ErrorResponse`: `detail: str`
    - `HealthResponse`: `status: Literal["ok", "degraded"]`, `service: str`, `detail: str | None = None`
    - _Requirements: 3.3, 3.4, 3.5, 7.1, 7.2, 6.1_

- [ ] 3. Implement the database layer
  - [ ] 3.1 Create `backend/db/database.py`
    - Define `DATABASE_URL` (default `sqlite:///./bright_bean.db`, overridable via env var)
    - Create `engine` with `connect_args={"check_same_thread": False}` for SQLite
    - Create `SessionLocal = sessionmaker(...)` and `Base = declarative_base()`
    - Implement `get_db()` generator dependency that yields a session and closes it after use
    - _Requirements: 3.1, 3.8_

  - [ ] 3.2 Create `backend/db/models.py` with `ContactMessageORM` SQLAlchemy model
    - Table `contact_messages`; columns: `id` (PK autoincrement), `name` (String 100), `email` (String 254), `subject` (String 150), `message` (Text), `submitted_at` (DateTime, default `datetime.utcnow`)
    - _Requirements: 3.2_

- [ ] 4. Implement in-memory data stores and seed logic
  - [ ] 4.1 Create `backend/data/store.py` with module-level `_menu_items: dict[int, MenuItem]` and `_gallery_items: dict[int, GalleryItem]`
    - Implement `seed_menu(path: str) -> None`: read and JSON-parse `data/menu.json`, validate each entry against `MenuItem`, populate `_menu_items`; log error and raise `SystemExit(1)` on missing file or invalid JSON
    - Implement `seed_gallery(items: list[dict]) -> None`: clear then refill `_gallery_items` from the provided list (idempotent)
    - Implement `get_menu_items(category: str | None) -> list[MenuItem]`: return all items when category is `None` or `"All"`, else exact case-sensitive filter
    - Implement `get_menu_item(id: int) -> MenuItem | None`
    - Implement `get_gallery_items(category: str | None) -> list[GalleryItem]`: same filter semantics as menu
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 1.7, 4.1, 4.2, 4.3, 4.4, 4.6_

  - [ ] 4.2 Create `backend/seeds/gallery_seed.py` with `GALLERY_ITEMS` list of dicts
    - Mirror the gallery data from `gallery.html` (id, category, image path relative to frontend root, label)
    - _Requirements: 4.6_

  - [ ]* 4.3 Write property test for category filter completeness — menu (Property 1)
    - **Property 1: Category filter completeness — menu**
    - Seed the store with generated `items`, call `get_menu_items(category)`, assert result equals exactly the items whose `category` field equals `category`
    - **Validates: Requirements 1.2, 1.7**

  - [ ]* 4.4 Write property test for MenuItem schema completeness (Property 2)
    - **Property 2: MenuItem schema completeness**
    - Seed the store with generated `items`, call `get_menu_items(None)`, assert every returned item has all required fields present, correctly typed, and within constraints
    - **Validates: Requirements 1.5**

  - [ ]* 4.5 Write property test for category filter completeness — gallery (Property 8)
    - **Property 8: Category filter completeness — gallery**
    - Seed the store with generated `items`, call `get_gallery_items(category)`, assert result equals exactly the items whose `category` field equals `category`
    - **Validates: Requirements 4.2, 4.4**

  - [ ]* 4.6 Write property test for GalleryItem schema completeness (Property 9)
    - **Property 9: GalleryItem schema completeness**
    - Seed the store with generated `items`, call `get_gallery_items(None)`, assert every returned item has all required fields present and non-empty
    - **Validates: Requirements 4.5**

  - [ ]* 4.7 Write unit tests for `store.py`
    - Test `seed_menu()` raises `SystemExit` on missing file and on invalid JSON
    - Test `seed_gallery()` idempotency: call twice with same list, assert `_gallery_items` count unchanged
    - Test `get_menu_items("All")` and `get_menu_items(None)` both return all items
    - Test `get_menu_item(id)` returns `None` for unknown id
    - _Requirements: 1.3, 1.6, 4.6_

- [ ] 5. Checkpoint — ensure store and model unit tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement API routers
  - [ ] 6.1 Create `backend/routers/menu.py`
    - `GET /api/menu`: optional `category: str = None` query param; delegate to `store.get_menu_items(category)`; return `list[MenuItem]` with 200
    - `GET /api/menu/{id}`: positive `int` path param; delegate to `store.get_menu_item(id)`; raise `HTTPException(404)` if not found; FastAPI handles 422 automatically for non-positive or non-integer ids
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.7, 1.8, 2.1, 2.2, 2.3, 2.4_

  - [ ] 6.2 Create `backend/routers/contact.py`
    - `POST /api/contact`: accept `ContactMessage` body; open DB session via `get_db`; create `ContactMessageORM` row; commit; return 201 with `{"message": "Message received", "id": <new_id>}`; on `SQLAlchemyError` rollback and return 503
    - `GET /api/contact`: query all rows ordered by `submitted_at DESC`; return `list[ContactMessageResponse]` with 200
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [ ] 6.3 Create `backend/routers/gallery.py`
    - `GET /api/gallery`: optional `category: str = None` query param; delegate to `store.get_gallery_items(category)`; return `list[GalleryItem]` with 200
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 6.4 Create `backend/routers/health.py`
    - `GET /health`: probe SQLite with `SELECT 1` via a DB session from `get_db`; on success return `HealthResponse(status="ok", service="bright-bean-api")` with 200; on `SQLAlchemyError` return 503 with `HealthResponse(status="degraded", detail="Database unreachable")`
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 7. Implement app factory and global error handlers
  - [ ] 7.1 Create `backend/main.py`
    - Instantiate `FastAPI()` app
    - Register `CORSMiddleware`: `allow_origins` = `["http://localhost", "http://127.0.0.1"]` plus any origins from `ALLOWED_ORIGINS` env var (comma-separated); `allow_methods=["GET","POST","OPTIONS"]`; `allow_headers=["*"]`; `allow_credentials=False`
    - Register global exception handlers: `RequestValidationError` → 422 `{"detail": "..."}` (flattened); `json.JSONDecodeError` / `UnicodeDecodeError` → 400 `{"detail": "Request body is not valid JSON"}`; bare `Exception` → 500 `{"detail": "Internal server error"}` (log with `logging.exception`, no stack trace in response)
    - Register `@app.on_event("startup")`: call `seed_menu(path_to_menu_json)`, `seed_gallery(GALLERY_ITEMS)`, `Base.metadata.create_all(bind=engine)`
    - Include routers: `menu_router` and `contact_router` with prefix `/api`, `gallery_router` with prefix `/api`, `health_router` with no prefix
    - Mount `StaticFiles(directory=cafe_root, html=True)` at `"/"` after all routes are registered
    - _Requirements: 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 8. Write integration tests
  - [ ] 8.1 Create `backend/tests/conftest.py`
    - `tmp_db` fixture: create in-memory SQLite engine, create all tables, yield a `SessionLocal` bound to it, drop all after test
    - `client` fixture: override `get_db` dependency with `tmp_db`; seed in-memory stores with known test data; yield `TestClient(app)`; clear overrides
    - _Requirements: all_

  - [ ]* 8.2 Write integration tests for menu endpoints
    - `GET /api/menu` → 200, all seeded items returned
    - `GET /api/menu?category=All` → 200, all items
    - `GET /api/menu?category=Coffee` → 200, only Coffee items
    - `GET /api/menu?category=Nonexistent` → 200, empty array
    - `GET /api/menu/{id}` with valid id → 200, correct item
    - `GET /api/menu/9999` → 404 with `detail` field
    - `GET /api/menu/0`, `GET /api/menu/-1` → 422
    - `GET /api/menu/abc` → 422
    - _Requirements: 1.1, 1.2, 1.3, 1.7, 1.8, 2.1, 2.2, 2.3, 2.4_

  - [ ]* 8.3 Write integration tests for contact endpoints
    - `POST /api/contact` with valid body → 201, response contains `message` and `id`
    - `POST /api/contact` with whitespace-only `name` → 422
    - `POST /api/contact` with invalid email → 422
    - `POST /api/contact` with malformed JSON → 400
    - `GET /api/contact` → 200, returns list ordered newest-first
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 8.4 Write integration tests for gallery and health endpoints
    - `GET /api/gallery` → 200, all seeded gallery items
    - `GET /api/gallery?category=All` → 200, all items
    - `GET /api/gallery?category=Café` → 200, filtered items
    - `GET /health` → 200, `status: "ok"`, `service: "bright-bean-api"`
    - `GET /health` with mocked DB failure → 503, `status: "degraded"`
    - OPTIONS preflight on `/api/menu` → 200 with CORS headers
    - _Requirements: 4.1, 4.2, 4.3, 5.2, 6.1, 6.2, 6.3_

  - [ ]* 8.5 Write integration tests for static file serving
    - Request `/index.html` → 200, `Content-Type: text/html`
    - Request `/css/menu.css` → 200, `Content-Type: text/css`
    - Request `/nonexistent.html` → 404
    - Request `/api/nonexistent` → JSON 404 (not static resolution)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 9. Write property-based tests for HTTP layer (Hypothesis)
  - [ ]* 9.1 Write property test for single item lookup round-trip via HTTP (Property 3)
    - **Property 3: Single item lookup round-trip**
    - For any generated `MenuItem`, seed the store with it, call `GET /api/menu/{item.id}`, assert response body is structurally and value-equal to the seeded item
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 9.2 Write property test for contact submission round-trip via HTTP (Property 4)
    - **Property 4: Contact submission round-trip**
    - For any valid generated `ContactMessage`, `POST /api/contact` then `GET /api/contact`, assert the list includes a record matching all submitted fields
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 9.3 Write property test for contact submission ordering invariant via HTTP (Property 5)
    - **Property 5: Contact submission ordering invariant**
    - For any sequence of valid `ContactMessage` submissions, assert `GET /api/contact` returns them ordered by `submitted_at` descending
    - **Validates: Requirements 3.6**

  - [ ]* 9.4 Write property test for whitespace-only field rejection via HTTP (Property 6)
    - **Property 6: Whitespace-only fields are rejected**
    - For any whitespace-only string in `name`, `subject`, or `message`, assert `POST /api/contact` returns 422 and contact count is unchanged
    - **Validates: Requirements 3.4, 3.5**

  - [ ]* 9.5 Write property test for invalid email rejection via HTTP (Property 7)
    - **Property 7: Invalid email addresses are rejected**
    - For any string without a valid email format, assert `POST /api/contact` returns 422
    - **Validates: Requirements 3.3, 3.5**

  - [ ]* 9.6 Write property test for error response Content-Type header (Property 10)
    - **Property 10: Error responses always carry `Content-Type: application/json`**
    - For any request to any `/api/*` endpoint that produces a 4xx or 5xx, assert `Content-Type: application/json` header is present and body contains a `detail` field
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**

- [ ] 10. Final checkpoint — ensure all tests pass
  - Run `pytest backend/tests/` and ensure all tests pass. Ask the user if any questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major phase
- Properties 1–10 from the design are each covered by a dedicated property-based test (tasks 4.3–4.6 and 9.1–9.6)
- In-memory stores (`_menu_items`, `_gallery_items`) must be module-level singletons; tests that mutate them should save and restore state or reinitialise via `seed_*` calls
- SQLite uses `check_same_thread=False` for FastAPI's async compatibility; tests use `sqlite:///:memory:` for full isolation
- The `StaticFiles` mount must be registered **after** all route handlers in `main.py` so `/api/*` routes take precedence
- `ALLOWED_ORIGINS` env var allows production CORS origins to be injected without code changes
- The `seed_menu()` path should be resolved relative to the workspace root so the server can be started from any working directory

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "2.2", "2.3", "3.1", "3.2"] },
    { "id": 1, "tasks": ["4.1", "4.2"] },
    { "id": 2, "tasks": ["4.3", "4.4", "4.5", "4.6", "4.7", "6.1", "6.2", "6.3", "6.4"] },
    { "id": 3, "tasks": ["7.1", "8.1"] },
    { "id": 4, "tasks": ["8.2", "8.3", "8.4", "8.5", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6"] }
  ]
}
```
