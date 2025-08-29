import datetime as dt
from pathlib import Path

MONGO_URI = "mongodb+srv://uttamvadher44_db_user:ofPQxUVlAuC26VFR@cluster0.9pym83c.mongodb.net/"
DB_PATH = "stocks.db"

# Directories
DAILY_JSON_DIR = Path("data/daily_json")
DAILY_REPORT_DIR = Path("reports/daily")
WEEKLY_REPORT_DIR = Path("reports/weekly")

for d in [DAILY_JSON_DIR, DAILY_REPORT_DIR, WEEKLY_REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TODAY = dt.date.today().strftime("%Y-%m-%d")
