"""
Run this to diagnose what's wrong:
    python d:\backend\cafe\cafe\diagnose.py
"""
import sys, os
print("=" * 55)
print("  Bright Bean Cafe - Diagnostic")
print("=" * 55)
print(f"\nPython: {sys.version}")
print(f"Working dir: {os.getcwd()}")

ROOT = r"d:\backend\cafe\cafe"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
print(f"Changed to: {os.getcwd()}")

# Check packages
print("\n--- Package check ---")
packages = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "sqlalchemy": "sqlalchemy",
    "pydantic": "pydantic",
    "email_validator": "email_validator",
}
missing = []
for name, imp in packages.items():
    try:
        mod = __import__(imp)
        ver = getattr(mod, "__version__", "?")
        print(f"  OK  {name} {ver}")
    except ImportError as e:
        print(f"  MISSING  {name}: {e}")
        missing.append(name)

if missing:
    print(f"\n  >>> NEED TO INSTALL: {missing}")
    print("  Run: pip install fastapi uvicorn[standard] pydantic[email] sqlalchemy email-validator --only-binary :all:")
    sys.exit(1)

# Check imports
print("\n--- Import check ---")
errors = []
modules = [
    "backend.db.database",
    "backend.db.models",
    "backend.models.menu",
    "backend.models.gallery",
    "backend.models.contact",
    "backend.models.order",
    "backend.data.store",
    "backend.seeds.gallery_seed",
    "backend.routers.menu",
    "backend.routers.contact",
    "backend.routers.gallery",
    "backend.routers.health",
    "backend.routers.orders",
    "backend.main",
]
for m in modules:
    try:
        __import__(m)
        print(f"  OK  {m}")
    except Exception as e:
        print(f"  ERROR  {m}: {e}")
        errors.append((m, str(e)))

# Check DB
print("\n--- Database check ---")
import sqlite3
db_path = os.path.join(ROOT, "bright_bean.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    conn.close()
    print(f"  DB exists. Tables: {tables}")
    needed = {"orders", "order_items", "contact_messages"}
    missing_tables = needed - set(tables)
    if missing_tables:
        print(f"  MISSING TABLES: {missing_tables}")
    else:
        # Check orders columns
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(orders)")
        cols = [r[1] for r in cur.fetchall()]
        conn.close()
        print(f"  orders columns: {cols}")
        needed_cols = {"customer_phone", "delivery_address", "order_type", "notes"}
        missing_cols = needed_cols - set(cols)
        if missing_cols:
            print(f"  MISSING COLUMNS in orders: {missing_cols}")
            print("  >>> DB SCHEMA IS OLD - needs reset")
        else:
            print("  Schema looks correct.")
else:
    print("  DB does not exist yet (will be created on first startup)")

print("\n--- Summary ---")
if errors:
    print(f"  IMPORT ERRORS: {len(errors)}")
    for m, e in errors:
        print(f"    {m}: {e}")
else:
    print("  All imports OK.")

print("\n  If everything above shows OK, run:")
print("  python d:\\backend\\cafe\\cafe\\run_cafe.py")
print("  Then open: http://127.0.0.1:8000")
