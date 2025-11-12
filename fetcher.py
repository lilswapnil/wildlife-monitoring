import time
import threading
import requests
from database import add_sighting, get_last_entry_id

# Try to load credentials, fallback to environment variables
try:
    from credentials import THINGSPEAK_READ_KEY, THINGSPEAK_CHANNEL_ID
except ImportError:
    print("Warning: Could not import credentials. Fetcher will not run.")
    THINGSPEAK_READ_KEY = None
    THINGSPEAK_CHANNEL_ID = None

THINGSPEAK_API_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"

def parse_feed_for_db(feed):
    """Parses a single feed from ThingSpeak into a dictionary suitable for the database."""
    try:
        return {
            'entry_id': feed.get('entry_id'),
            'timestamp': feed.get('created_at'),
            'motion': int(feed.get('field1', 0)),
            'distance': float(feed.get('field2', 0)) if feed.get('field2') else 0,
            'light_level': int(feed.get('field3', 0)) if feed.get('field3') else 0,
            'false_positive': int(feed.get('field4', 0)),
            'animal_code': int(feed.get('field5', 0)) if feed.get('field5') else 0,
        }
    except (ValueError, TypeError, KeyError):
        return None


def fetch_from_thingspeak():
    """Fetches new data from ThingSpeak and adds it to the database."""
    if not THINGSPEAK_READ_KEY or not THINGSPEAK_CHANNEL_ID:
        return

    print("Background fetcher: Checking for new data from ThingSpeak...")
    try:
        # We fetch all results and let the DB handle duplicates.
        # A more optimized way would be to fetch only new results,
        # but ThingSpeak API doesn't easily support "since entry_id".
        params = {'api_key': THINGSPEAK_READ_KEY, 'results': 8000}
        response = requests.get(THINGSPEAK_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        feeds = data.get('feeds', [])
        
        new_entries = 0
        last_id = get_last_entry_id()

        for feed in feeds:
            if feed['entry_id'] > last_id:
                parsed = parse_feed_for_db(feed)
                if parsed:
                    add_sighting(parsed)
                    new_entries += 1
        
        if new_entries > 0:
            print(f"Background fetcher: Added {new_entries} new sightings to the database.")
        else:
            print("Background fetcher: No new sightings found.")

    except requests.exceptions.RequestException as e:
        print(f"Background fetcher: Error fetching from ThingSpeak: {e}")
    except Exception as e:
        print(f"Background fetcher: An unexpected error occurred: {e}")


def start_fetcher():
    """Starts the background thread to periodically fetch data."""
    
    def fetch_loop():
        while True:
            fetch_from_thingspeak()
            # Wait for 60 seconds before the next fetch
            time.sleep(60)

    if THINGSPEAK_READ_KEY and THINGSPEAK_CHANNEL_ID:
        print("Starting background ThingSpeak fetcher...")
        thread = threading.Thread(target=fetch_loop, daemon=True)
        thread.start()
    else:
        print("Skipping background fetcher due to missing credentials.")
