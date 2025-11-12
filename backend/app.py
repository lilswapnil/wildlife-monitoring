"""
Wildlife Monitoring Web Application
Flask backend for visualizing ThingSpeak data
"""
from flask import Flask, render_template, jsonify
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

app = Flask(__name__)

# --- Configuration ---
# Animal type mapping (reverse of main.py)
ANIMAL_MAP = {
    0: "Unknown", 1: "Fox", 2: "Badger", 3: "Deer", 4: "Squirrel",
    5: "Rabbit", 6: "Hedgehog", 7: "Owl", 8: "Woodpecker", 9: "Boar",
    10: "Bear", 11: "Raccoon", 12: "Skunk", 13: "Lynx", 14: "Wolf", 15: "Moose",
}

# Try to load credentials, fallback to environment variables
try:
    from credentials import THINGSPEAK_READ_KEY, THINGSPEAK_CHANNEL_ID
except ImportError:
    THINGSPEAK_READ_KEY = os.getenv('THINGSPEAK_READ_KEY', '')
    THINGSPEAK_CHANNEL_ID = os.getenv('THINGSPEAK_CHANNEL_ID', '')

THINGSPEAK_API_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"

# --- Data Fetching and Processing ---

def fetch_thingspeak_data(results: int = 8000) -> Optional[List[Dict]]:
    """Fetch raw data from the ThingSpeak channel."""
    if not THINGSPEAK_READ_KEY or not THINGSPEAK_CHANNEL_ID:
        print("Error: ThingSpeak credentials not found.")
        return None
    
    try:
        params = {'api_key': THINGSPEAK_READ_KEY, 'results': results}
        response = requests.get(THINGSPEAK_API_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get('feeds', [])
    except requests.RequestException as e:
        print(f"Error fetching ThingSpeak data: {e}")
        return None

def parse_and_enrich_feed(feed: Dict) -> Optional[Dict]:
    """Parse a single feed entry and enrich it with computed data."""
    try:
        motion = int(feed.get('field1', 0) or 0)
        distance = float(feed.get('field2', 0) or 0)
        light_level = int(feed.get('field3', 0) or 0)
        false_positive = int(feed.get('field4', 0) or 0)
        animal_code = int(feed.get('field5', 0) or 0)

        if light_level < 1000: time_of_day = "Night"
        elif light_level > 3000: time_of_day = "Day"
        else: time_of_day = "Dawn/Dusk"

        return {
            'entry_id': feed.get('entry_id'),
            'timestamp': feed.get('created_at'),
            'motion': motion,
            'distance': distance,
            'light_level': light_level,
            'false_positive': bool(false_positive),
            'animal_type': ANIMAL_MAP.get(animal_code, "Unknown"),
            'animal_code': animal_code,
            'time_of_day': time_of_day,
            'is_valid_detection': motion == 1 and not bool(false_positive)
        }
    except (ValueError, TypeError, KeyError):
        return None

def process_all_feeds(feeds: List[Dict]) -> List[Dict]:
    """Parse and enrich a list of raw feeds."""
    parsed_feeds = [parse_and_enrich_feed(f) for f in feeds]
    return [f for f in parsed_feeds if f is not None]

def calculate_dashboard_stats(parsed_feeds: List[Dict]) -> Dict[str, Any]:
    """Calculate all statistics and chart data for the dashboard."""
    valid_detections = [f for f in parsed_feeds if f['is_valid_detection']]
    
    # Basic Stats
    total_detections = len([f for f in parsed_feeds if f['motion'] == 1])
    false_positives = total_detections - len(valid_detections)
    
    # Animal Counts for Pie Chart
    animal_counts = {}
    for feed in valid_detections:
        animal = feed['animal_type']
        animal_counts[animal] = animal_counts.get(animal, 0) + 1
    
    # Time of Day Distribution for Doughnut Chart
    time_distribution = {}
    for feed in valid_detections:
        tod = feed['time_of_day']
        time_distribution[tod] = time_distribution.get(tod, 0) + 1
        
    # Average Distance
    valid_distances = [f['distance'] for f in valid_detections if f['distance'] > 0]
    avg_distance = sum(valid_distances) / len(valid_distances) if valid_distances else 0

    # Proximity Over Time for Line Chart
    proximity_data = [
        {'x': f['timestamp'], 'y': f['distance']} 
        for f in valid_detections if f['distance'] > 0
    ]

    return {
        "stats": {
            "total_detections": total_detections,
            "valid_detections": len(valid_detections),
            "false_positives": false_positives,
            "animal_types": len(animal_counts),
            "average_distance": avg_distance,
        },
        "charts": {
            "animal_distribution": {
                "labels": list(animal_counts.keys()),
                "data": list(animal_counts.values())
            },
            "time_distribution": {
                "labels": list(time_distribution.keys()),
                "data": list(time_distribution.values())
            },
            "proximity_over_time": proximity_data
        },
        "timeline": parsed_feeds
    }

# --- Flask Routes ---

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/dashboard')
def get_dashboard_data():
    """A single, powerful endpoint to provide all data for the dashboard."""
    raw_feeds = fetch_thingspeak_data(results=8000)
    
    if raw_feeds is None:
        return jsonify({'error': 'Failed to fetch data from ThingSpeak.'}), 500
        
    parsed_feeds = process_all_feeds(raw_feeds)
    dashboard_data = calculate_dashboard_stats(parsed_feeds)
    
    return jsonify(dashboard_data)

if __name__ == '__main__':
    if not THINGSPEAK_READ_KEY or not THINGSPEAK_CHANNEL_ID:
        print("⚠️  Warning: ThingSpeak credentials not configured!")
        print("   Please create `credentials.py` or set environment variables.")
    
    port = int(os.getenv('PORT', 5001))
    print(f"🌐 Starting Forest Watch server on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)

