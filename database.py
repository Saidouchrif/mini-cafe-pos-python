import sqlite3
from pathlib import Path

DB_NAME = "cafe.db"

def get_conn():
    db_path = Path(DB_NAME)
    return sqlite3.connect(db_path)
