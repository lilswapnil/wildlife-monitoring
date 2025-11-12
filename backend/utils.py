# backend/utils.py
import requests
from datetime import datetime
import pytz

# Animal name mapping from the firmware
ANIMAL_NAMES = {
    1: "Fox", 2: "Badger", 3: "Deer", 4: "Squirrel", 5: "Rabbit",
    6: "Hedgehog", 7: "Owl", 8: "Woodpecker", 9: "Boar", 10: "Bear",
    11: "Raccoon", 12: "Skunk", 13: "Lynx", 14: "Wolf", 15: "Moose",
    0: "Unknown",
}

def fetch_new_thingspeak_data(channel_id, api_key, last_entry_id):
    """
    Fetches only new entries from ThingSpeak since the last known entry ID.
    """
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {
        "api_key": api_key,
        "results": 2500 
    }
    print(f"Fetching data from ThingSpeak starting after entry_id: {last_entry_id}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filter out feeds we already have
        new_feeds = [feed for feed in data.get('feeds', []) if int(feed['entry_id']) > last_entry_id]
        print(f"Found {len(new_feeds)} new entries in ThingSpeak.")
        return new_feeds
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from ThingSpeak: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing ThingSpeak response: {e}")
        return None

def process_feeds_for_db(feeds):
    """
    Processes raw ThingSpeak feed data into a structured format suitable for the database.
    """
    if not feeds:
        return []

    processed_feeds = []
    for feed in feeds:
        try:
            utc_time = datetime.strptime(feed['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
            
            hour = utc_time.hour
            if 5 <= hour < 12: time_of_day = "Morning"
            elif 12 <= hour < 17: time_of_day = "Afternoon"
            elif 17 <= hour < 21: time_of_day = "Evening"
            else: time_of_day = "Night"

            motion = int(feed.get('field1', 0) or 0)
            distance = float(feed.get('field2', 0) or 0)
            light = int(feed.get('field3', 0) or 0)
            is_false_positive = bool(int(feed.get('field4', 0) or 0))
            animal_id = int(feed.get('field5', 0) or 0)
            is_valid_detection = not is_false_positive and animal_id != 0

            processed_feeds.append({
                "entry_id": feed['entry_id'],
                "timestamp": utc_time.isoformat(),
                "motion": motion,
                "distance": distance,
                "light_level": light,
                "false_positive": is_false_positive,
                "animal_id": animal_id,
                "animal_type": ANIMAL_NAMES.get(animal_id, "Unknown"),
                "is_valid_detection": is_valid_detection,
                "time_of_day": time_of_day,
            })
        except (ValueError, TypeError, KeyError) as e:
            print(f"Skipping malformed feed entry {feed.get('entry_id', 'N/A')}: {e}")
            continue
            
    return processed_feeds

def calculate_dashboard_data(feeds):
    """
    Calculates all statistics and chart data from the processed feeds.
    This function now expects feeds already retrieved from our local DB.
    """
    valid_detections = [f for f in feeds if f['is_valid_detection']]
    
    # --- Basic Stats ---
    total_detections = len([f for f in feeds if f['motion'] == 1])
    total_valid_detections = len(valid_detections)
    avg_distance = sum(f['distance'] for f in valid_detections) / total_valid_detections if total_valid_detections > 0 else 0
    
    # --- Animal Distribution Chart ---
    animal_counts = {}
    for feed in valid_detections:
        animal_name = feed['animal_type']
        animal_counts[animal_name] = animal_counts.get(animal_name, 0) + 1
    
    # --- Time of Day Distribution Chart ---
    time_counts = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    for feed in valid_detections:
        time_counts[feed['time_of_day']] = time_counts.get(feed['time_of_day'], 0) + 1
        
    # --- Proximity Over Time Chart ---
    proximity_data = [
        {'x': feed['timestamp'], 'y': (feed['distance'] / 100)} # Convert cm to m
        for feed in valid_detections
    ]

    return {
        "stats": {
            "total_detections": total_detections,
            "valid_detections": total_valid_detections,
            "average_distance": avg_distance,
            "animal_types": len(animal_counts),
        },
        "charts": {
            "animal_distribution": {
                "labels": list(animal_counts.keys()),
                "data": list(animal_counts.values())
            },
            "time_distribution": {
                "labels": list(time_counts.keys()),
                "data": list(time_counts.values())
            },
            "proximity_over_time": proximity_data,
        },
        "timeline": feeds # The full, processed timeline
    }
