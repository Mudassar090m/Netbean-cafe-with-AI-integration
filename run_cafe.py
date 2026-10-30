"""
Bright Bean Cafe - Complete Startup Script
==========================================
Double-click this file in Windows Explorer, OR run:
    python run_cafe.py

This script:
  1. Checks Python packages are installed, installs missing ones
  2. Resets the database (drops old tables, creates new ones)
  3. Starts the server at http://127.0.0.1:8000
"""
import subprocess
import sys
import sqlite3
import os
from pathlib import Path

ROOT = Path(__file__).parent
os.chdir(ROOT)

print("=" * 50)
print("  Bright Bean Cafe - Backend Startup")
print("=" * 50)

# ── 1. Install dependencies if missing ───────────────────────────────────────
print("\n[1/3] Checking dependencies...")
REQUIRED = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "email_validator"]
missing = []
for pkg in REQUIRED:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"  Installing: {missing}")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "fastapi", "uvicorn[standard]", "pydantic[email]",
        "sqlalchemy", "email-validator",
        "--only-binary", ":all:", "-q"
    ])
    print("  Done.")
else:
    print("  All packages present.")

# ── 2. Reset database ─────────────────────────────────────────────────────────
print("\n[2/3] Resetting database...")
DB = ROOT / "bright_bean.db"

# Drop all tables via raw sqlite3 (no imports needed)
conn = sqlite3.connect(str(DB))
conn.execute("PRAGMA foreign_keys = OFF")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
old_tables = [r[0] for r in cur.fetchall()]
for t in old_tables:
    conn.execute(f"DROP TABLE IF EXISTS [{t}]")
conn.commit()
conn.close()
print(f"  Dropped old tables: {old_tables or 'none'}")

# Recreate with current schema
sys.path.insert(0, str(ROOT))
from backend.db.database import Base, engine
import backend.db.models  # registers all ORM models with metadata
Base.metadata.create_all(bind=engine)

import sqlalchemy
new_tables = sqlalchemy.inspect(engine).get_table_names()
print(f"  Created tables: {new_tables}")
print("  Database ready.")

# ── 3. Start server ───────────────────────────────────────────────────────────
print("\n[3/3] Starting server...")
print("\n  ✓ Open your browser: http://127.0.0.1:8000")
print("  ✓ API docs:          http://127.0.0.1:8000/docs")
print("  ✓ Menu page:         http://127.0.0.1:8000/html/menu.html")
print("  ✓ Orders:            http://127.0.0.1:8000/api/orders")
print("\n  Press Ctrl+C to stop.\n")

subprocess.run([
    sys.executable, "-m", "uvicorn", "backend.main:app",
    "--reload", "--port", "8000", "--host", "127.0.0.1"
])
