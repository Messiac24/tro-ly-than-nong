import sys
import os
from pathlib import Path

BASE_DIR = Path(r"d:\AI_nong_san")
SERVER_DIR = BASE_DIR / "server"

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(SERVER_DIR))

print("sys.path:")
for p in sys.path:
    print(f"  {p}")

try:
    import database
    print(f"Successfully imported database from: {database.__file__}")
    from database import SessionLocal
    print("Successfully imported SessionLocal")
except ImportError as e:
    print(f"Failed to import database: {e}")

try:
    import models
    print(f"Successfully imported models from: {models.__file__}")
except ImportError as e:
    print(f"Failed to import models: {e}")
