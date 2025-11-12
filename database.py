import sqlite3
import threading
from contextlib import contextmanager

DATABASE = 'wildlife.db'
db_lock = threading.Lock()

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the database and creates the sightings table if it doesn't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sightings (
                entry_id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                motion INTEGER NOT NULL,
                distance REAL NOT NULL,
                light_level INTEGER NOT NULL,
                false_positive INTEGER NOT NULL,
                animal_id INTEGER NOT NULL
            )
        ''')
        conn.commit()
        print("Database initialized.")

def add_sighting(feed):
    """Adds a new sighting to the database, ignoring duplicates."""
    with db_lock:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sightings (entry_id, timestamp, motion, distance, light_level, false_positive, animal_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feed['entry_id'],
                    feed['timestamp'],
                    feed['motion'],
                    feed['distance'],
                    feed['light_level'],
                    1 if feed['false_positive'] else 0,
                    feed['animal_code']
                )
            )
            conn.commit()

def get_last_entry_id():
    """Gets the ID of the most recent entry in the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(entry_id) FROM sightings")
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
