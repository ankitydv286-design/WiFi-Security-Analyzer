from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "wifi_monitor.db"
SCAN_TIMEOUT_SECONDS = 2
