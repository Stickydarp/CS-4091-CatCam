import sqlite3
from datetime import datetime
import os

DB_FILE = "db.sqlite3"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cameraId INTEGER,
                file_type TEXT,
                classification TEXT,
                classified BOOLEAN
                confidence FLOAT
            )
        ''')
        conn.commit()
        conn.close()

def insert_metadata(filename: str, description: str = None) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO images (filename, description) VALUES (?, ?)",
        (filename, description)
    )
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    return image_id

def get_all_metadata() -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, timestamp, description FROM images")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row[0], "filename": row[1], "timestamp": row[2], "description": row[3]}
        for row in rows
    ]

def delete_metadata(image_id: int) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        filename = row[0]
        filepath = os.path.join("images", filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False
