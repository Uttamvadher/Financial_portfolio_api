import sqlite3
import pandas as pd
import datetime as dt
from pymongo import MongoClient
from config import DB_PATH, DAILY_JSON_DIR, MONGO_URI

def save_to_sql(df: pd.DataFrame):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("daily_stocks", conn, if_exists="append", index=False)
    conn.close()

def save_to_json(df: pd.DataFrame):
    date_str = dt.datetime.now().strftime("%Y-%m-%d")
    file_name = DAILY_JSON_DIR / f"stocks_{date_str}.json"
    df.to_json(file_name, orient="records", indent=2, date_format="iso")
    return str(file_name)

def save_to_mongo(df: pd.DataFrame):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["finance"]
        collection = db["daily_stocks"]
        payload = df.to_dict(orient="records")
        if payload:
            collection.insert_many(payload)
        return "Inserted into MongoDB"
    except Exception as e:
        return f"MongoDB insert skipped: {e}"
