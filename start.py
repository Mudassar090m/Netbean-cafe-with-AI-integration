"""
Bright Bean Café — one-shot startup helper.

Run this ONCE after any schema change, then use uvicorn directly after that.

    python start.py

What it does:
  1. Drops ALL existing tables (safe — wipes orders/contacts, keeps nothing)
  2. Recreates tables with the latest schema via SQLAlchemy create_all
  3. Starts uvicorn on port 8000
"""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DB   = ROOT / "bright_bean.db"

# Always run from the project root so sqlite:///./bright_bean.db resolves correctly
os.chdir(ROOT)

# ── 1. Drop all tables ────────────────────────────────────────────────────────
print("Resetting database …")
conn = sqlite3.connect(str(DB))
conn.execute("PRAGMA foreign_keys = OFF")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
for t in tables:
    conn.execute(f"DROP TABLE IF EXISTS [{t}]")
conn.commit()
conn.close()
print(f"  Dropped: {tables or '(none)'}")

# ── 2. Recreate with current schema ──────────────────────────────────────────
sys.path.insert(0, str(ROOT))

from backend.db.database import Base, engine
import backend.db.models   # registers ContactMessageORM, OrderORM, OrderItemORM
Base.metadata.create_all(bind=engine)

import sqlalchemy
tables_now = sqlalchemy.inspect(engine).get_table_names()
print(f"  Created: {tables_now}")
print("Database ready.\n")

# ── 3. Start the server ───────────────────────────────────────────────────────
print("Starting server on http://127.0.0.1:8000 …")
print("Press Ctrl+C to stop.\n")
subprocess.run(
    [sys.executable, "-m", "uvicorn", "backend.main:app",
     "--reload", "--port", "8000"],
    cwd=str(ROOT),
)
