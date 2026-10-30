# Bright Bean Café — FastAPI Backend

REST API backend for the Bright Bean Café static frontend. Serves menu, gallery, and contact data via JSON endpoints and also mounts the existing HTML/CSS/JS frontend so everything runs from a single server.

## Quick start

```bash
# Install dependencies (Python 3.11+ recommended; 3.14 requires --only-binary)
pip install -r backend/requirements.txt --only-binary :all:

# Run the server (from the cafe/ root directory)
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000 to see the frontend. The API is at http://localhost:8000/api/.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/menu` | All menu items (optional `?category=` filter) |
| GET | `/api/menu/{id}` | Single menu item by id |
| POST | `/api/contact` | Submit a contact form message |
| GET | `/api/contact` | All contact submissions (newest first) |
| GET | `/api/gallery` | All gallery items (optional `?category=` filter) |
| GET | `/health` | Health check |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./bright_bean.db` | SQLAlchemy database URL |
| `ALLOWED_ORIGINS` | _(none)_ | Comma-separated extra CORS origins for production |

## Running tests

```bash
# From the cafe/ root directory
python -m pytest backend/tests/ -v
```

The suite covers 58 tests across three files:
- `test_store.py` — unit and Hypothesis property tests for the in-memory store
- `test_integration.py` — full HTTP integration tests for all endpoints
- `test_properties_http.py` — Hypothesis property-based HTTP tests (Properties 3–7, 10)
