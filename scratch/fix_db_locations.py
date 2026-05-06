import sys
import os
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = BASE_DIR / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from server.database import SessionLocal
from server import models

def fix_locations():
    db = SessionLocal()
    
    # Update to "Phường B'Lao"
    db.query(models.SearchHistory).filter(
        models.SearchHistory.location.like("%B'Lao%")
    ).update({"location": "Phường B'Lao"}, synchronize_session=False)

    # Update to "Phường Xuân Trường"
    db.query(models.SearchHistory).filter(
        models.SearchHistory.location.like("%Trạm Hành%")
    ).update({"location": "Phường Xuân Trường"}, synchronize_session=False)

    db.query(models.SearchHistory).filter(
        models.SearchHistory.location.like("%Xuân Trường%")
    ).update({"location": "Phường Xuân Trường"}, synchronize_session=False)

    db.commit()
    db.close()
    print("Fixed locations in SearchHistory")

if __name__ == "__main__":
    fix_locations()
