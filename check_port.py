"""Check if port 8000 is available and test the server."""
import socket
import subprocess
import sys
import os

print("Checking port 8000...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8000))
sock.close()

if result == 0:
    print("  Port 8000 IS open — server is already running!")
    print("  Go to: http://127.0.0.1:8000/html/menu.html")
else:
    print("  Port 8000 is NOT open — server is NOT running.")
    print("")
    print("  Starting server now...")
    os.chdir(r"d:\backend\cafe\cafe")
    sys.path.insert(0, r"d:\backend\cafe\cafe")
    
    # Start server directly (blocking - keep this window open)
    subprocess.run([
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--port", "8000", "--host", "127.0.0.1"
    ], cwd=r"d:\backend\cafe\cafe")
