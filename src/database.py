import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "queue.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                scheduled_time TEXT NOT NULL,
                created_at TEXT NOT NULL,
                published_at TEXT,
                error_msg TEXT
            )
        """)
        conn.commit()

def add_to_queue(item_type, content, scheduled_time):
    init_db()
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO content_queue (type, content, status, scheduled_time, created_at)
            VALUES (?, ?, 'pending', ?, ?)
        """, (item_type, content, scheduled_time, created_at))
        conn.commit()

def get_pending_items():
    init_db()
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, type, content, scheduled_time FROM content_queue
            WHERE status = 'pending' AND scheduled_time <= ?
        """, (now,))
        return cursor.fetchall()

def mark_as_published(item_id):
    published_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE content_queue
            SET status = 'published', published_at = ?, error_msg = NULL
            WHERE id = ?
        """, (published_at, item_id))
        conn.commit()

def mark_as_failed(item_id, error_msg):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE content_queue
            SET status = 'failed', error_msg = ?
            WHERE id = ?
        """, (error_msg, item_id))
        conn.commit()

def get_all_items():
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, type, status, scheduled_time, created_at, published_at, error_msg 
            FROM content_queue
            ORDER BY scheduled_time ASC
        """)
        return cursor.fetchall()
