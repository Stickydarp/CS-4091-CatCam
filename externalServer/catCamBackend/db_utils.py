import sqlite3
from datetime import datetime
import os

DB_FILE = "/catCamData/metadata/db.sqlite3"

IMAGES_DIR = "/catCamData/images"

def init_db():
    # Ensure directories exist
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

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
                classified BOOLEAN,
                confidence FLOAT
            )
        ''')
        conn.commit()
        conn.close()

def insert_metadata(
    filename: str,
    cameraId: int = None,
    file_type: str = None,
    classification: str = None,
    classified: bool = False,
    confidence: float = None
) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO images (
            filename, cameraId, file_type, classification, classified, confidence
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (filename, cameraId, file_type, classification, classified, confidence)
    )
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    return image_id

def get_all_metadata() -> list[dict]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, timestamp, cameraId, file_type, classification, classified, confidence FROM images"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "filename": row[1],
            "timestamp": row[2],
            "cameraId": row[3],
            "file_type": row[4],
            "classification": row[5],
            "classified": bool(row[6]),
            "confidence": row[7]
        }
        for row in rows
    ]


def get_metadata_by_id(image_id: int) -> dict | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, timestamp, cameraId, file_type, classification, classified, confidence FROM images WHERE id = ?",
        (image_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "filename": row[1],
        "timestamp": row[2],
        "cameraId": row[3],
        "file_type": row[4],
        "classification": row[5],
        "classified": bool(row[6]),
        "confidence": row[7]
    }


def update_metadata(image_id: int, *, filename: str = None, cameraId: int = None, file_type: str = None, classification: str = None, classified: bool = None, confidence: float = None) -> bool:
    # Build dynamic update
    fields = {}
    if filename is not None:
        fields['filename'] = filename
    if cameraId is not None:
        fields['cameraId'] = cameraId
    if file_type is not None:
        fields['file_type'] = file_type
    if classification is not None:
        fields['classification'] = classification
    if classified is not None:
        fields['classified'] = int(bool(classified))
    if confidence is not None:
        fields['confidence'] = confidence

    if not fields:
        return False

    set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values())
    values.append(image_id)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE images SET {set_clause} WHERE id = ?", values)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_metadata(image_id: int) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    if row:
        filename = row[0]
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def get_image_path_by_id(image_id: int) -> str | None:
    """Return the absolute path to the image file for a given id, or None if missing."""
    meta = get_metadata_by_id(image_id)
    if not meta:
        return None
    return os.path.join(IMAGES_DIR, meta['filename'])


def query_images(classified: bool | None = None, cameraId: int | None = None, since: str | None = None, before: str | None = None, limit: int | None = None) -> list[dict]:
    """Query images with simple filters. since/before expect ISO-like strings or partial SQL DATETIME compatible strings.

    This is a thin helper around SQL SELECT and returns the same metadata dicts as get_all_metadata.
    """
    q = "SELECT id, filename, timestamp, cameraId, file_type, classification, classified, confidence FROM images"
    clauses = []
    params = []
    if classified is not None:
        clauses.append("classified = ?")
        params.append(int(bool(classified)))
    if cameraId is not None:
        clauses.append("cameraId = ?")
        params.append(cameraId)
    if since is not None:
        clauses.append("timestamp >= ?")
        params.append(since)
    if before is not None:
        clauses.append("timestamp <= ?")
        params.append(before)

    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY timestamp DESC"
    if limit is not None:
        q += f" LIMIT {int(limit)}"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(q, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "filename": row[1],
            "timestamp": row[2],
            "cameraId": row[3],
            "file_type": row[4],
            "classification": row[5],
            "classified": bool(row[6]),
            "confidence": row[7]
        }
        for row in rows
    ]
