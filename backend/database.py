# backend/database.py
import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'wildlife.db')

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the sightings table if it doesn't exist."""
    if os.path.exists(DATABASE_FILE):
        print("Database already exists.")
        return
        
    print("Initializing new database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE sightings (
            entry_id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            motion INTEGER NOT NULL,
            distance REAL,
            light_level INTEGER,
            false_positive INTEGER NOT NULL,
            animal_id INTEGER,
            animal_type TEXT,
            is_valid_detection INTEGER NOT NULL,
            time_of_day TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized and 'sightings' table created.")

def get_latest_entry_id():
    """Finds the most recent entry_id stored in the local database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(entry_id) FROM sightings')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] is not None else 0

def bulk_insert_sightings(sighting_data):
    """
    Inserts a list of sighting dictionaries into the database.
    Expects a list of dicts, where each dict matches the table schema.
    """
    if not sighting_data:
        return 0
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Prepare data for executemany
    insert_data = [
        (
            s['entry_id'], s['timestamp'], s['motion'], s['distance'],
            s['light_level'], 1 if s['false_positive'] else 0, s['animal_id'],
            s['animal_type'], 1 if s['is_valid_detection'] else 0, s['time_of_day']
        )
        for s in sighting_data
    ]
    
    try:
        cursor.executemany('''
            INSERT INTO sightings (
                entry_id, timestamp, motion, distance, light_level, 
                false_positive, animal_id, animal_type, is_valid_detection, time_of_day
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', insert_data)
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} new sightings.")
        return cursor.rowcount
    except sqlite3.IntegrityError as e:
        print(f"Database integrity error during bulk insert: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def get_all_sightings():
    """Retrieves all sightings from the local database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sightings ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    # Convert rows to a list of dictionaries
    return [dict(row) for row in rows]
