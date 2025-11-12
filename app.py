"""
Wildlife Monitoring Web Application
Flask backend for visualizing ThingSpeak data
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

app = Flask(__name__)
CORS(app)

# Animal type mapping (reverse of main.py)
ANIMAL_MAP = {
    0: "Unknown",
    1: "Fox", 2: "Badger", 3: "Deer", 4: "Squirrel", 5: "Rabbit",
    6: "Hedgehog", 7: "Owl", 8: "Woodpecker", 9: "Boar", 10: "Bear",
    11: "Raccoon", 12: "Skunk", 13: "Lynx", 14: "Wolf", 15: "Moose",
}

# Try to load credentials, fallback to environment variables
try:
    from credentials import THINGSPEAK_READ_KEY, THINGSPEAK_CHANNEL_ID
except ImportError:
    THINGSPEAK_READ_KEY = os.getenv('THINGSPEAK_READ_KEY', '')
    THINGSPEAK_CHANNEL_ID = os.getenv('THINGSPEAK_CHANNEL_ID', '')

THINGSPEAK_API_URL = "https://api.thingspeak.com/channels/{}/feeds.json"


def fetch_thingspeak_data(results: int = 100) -> Optional[Dict]:
    """
    Fetch data from ThingSpeak channel
    
    Args:
        results: Number of results to fetch (max 8000)
    
    Returns:
        Dictionary containing channel info and feeds, or None if error
    """
    if not THINGSPEAK_READ_KEY or not THINGSPEAK_CHANNEL_ID:
        return None
    
    try:
        url = THINGSPEAK_API_URL.format(THINGSPEAK_CHANNEL_ID)
        params = {
            'api_key': THINGSPEAK_READ_KEY,
            'results': results
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching ThingSpeak data: {e}")
        return None


def parse_feeds(feeds: List[Dict]) -> List[Dict]:
    """
    Parse and enrich feed data with human-readable information
    
    Args:
        feeds: List of feed dictionaries from ThingSpeak
    
    Returns:
        List of enriched feed dictionaries
    """
    parsed = []
    
    for feed in feeds:
        try:
            # Parse fields
            motion = int(feed.get('field1', 0))
            distance = float(feed.get('field2', 0)) if feed.get('field2') else 0
            light_level = int(feed.get('field3', 0)) if feed.get('field3') else 0
            false_positive = int(feed.get('field4', 0))
            animal_code = int(feed.get('field5', 0)) if feed.get('field5') else 0
            
            # Determine time of day based on light level
            if light_level < 1000:
                time_of_day = "Night"
            elif light_level > 3000:
                time_of_day = "Day"
            else:
                time_of_day = "Dawn/Dusk"
            
            # Get animal name
            animal_type = ANIMAL_MAP.get(animal_code, "Unknown")
            
            parsed.append({
                'entry_id': feed.get('entry_id'),
                'timestamp': feed.get('created_at'),
                'motion': motion,
                'distance': distance,
                'light_level': light_level,
                'false_positive': bool(false_positive),
                'animal_type': animal_type,
                'animal_code': animal_code,
                'time_of_day': time_of_day,
                'is_valid_detection': motion == 1 and not bool(false_positive)
            })
        except (ValueError, KeyError) as e:
            print(f"Error parsing feed: {e}")
            continue
    
    return parsed


@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    """
    API endpoint to fetch and return ThingSpeak data
    
    Returns:
        JSON response with channel info and parsed feeds
    """
    data = fetch_thingspeak_data(results=200) # Fetch more results for better timeline
    
    if not data:
        return jsonify({
            'error': 'Unable to fetch data. Please check your ThingSpeak configuration.',
            'channel': None,
            'feeds': [],
        }), 200
    
    feeds = data.get('feeds', [])
    parsed_feeds = parse_feeds(feeds)
    
    return jsonify({
        'channel': data.get('channel', {}),
        'feeds': parsed_feeds,
    })


@app.route('/api/stats')
def get_stats():
    """
    API endpoint to get statistics about detections
    
    Returns:
        JSON response with statistics
    """
    data = fetch_thingspeak_data(results=8000)  # Get more data for stats
    
    if not data:
        return jsonify({
            'error': 'Unable to fetch data for statistics.',
            'total_detections': 0,
            'valid_detections': 0,
            'false_positives': 0,
            'animal_counts': {},
            'time_distribution': {},
            'average_distance': 0,
            'total_records': 0
        }), 200  # Return 200 even with error so frontend can handle it
    
    feeds = data.get('feeds', [])
    parsed_feeds = parse_feeds(feeds)
    
    # Calculate statistics
    total_detections = len([f for f in parsed_feeds if f['motion'] == 1])
    valid_detections = len([f for f in parsed_feeds if f['is_valid_detection']])
    false_positives = len([f for f in parsed_feeds if f['false_positive']])
    
    # Animal type counts
    animal_counts = {}
    for feed in parsed_feeds:
        if feed['is_valid_detection']:
            animal = feed['animal_type']
            animal_counts[animal] = animal_counts.get(animal, 0) + 1
    
    # Time of day distribution
    time_distribution = {}
    for feed in parsed_feeds:
        if feed['is_valid_detection']:
            tod = feed['time_of_day']
            time_distribution[tod] = time_distribution.get(tod, 0) + 1
    
    # Average distance for valid detections
    valid_distances = [f['distance'] for f in parsed_feeds if f['is_valid_detection'] and f['distance'] > 0]
    avg_distance = sum(valid_distances) / len(valid_distances) if valid_distances else 0
    
    return jsonify({
        'total_detections': total_detections,
        'valid_detections': valid_detections,
        'false_positives': false_positives,
        'animal_counts': animal_counts,
        'time_distribution': time_distribution,
        'average_distance': round(avg_distance, 2),
        'total_records': len(parsed_feeds)
    })


@app.route('/api/latest')
def get_latest():
    """
    API endpoint to get the latest detection
    
    Returns:
        JSON response with the most recent detection
    """
    data = fetch_thingspeak_data(results=1)
    
    if not data:
        return jsonify({
            'error': 'Unable to fetch latest data.'
        }), 500
    
    feeds = data.get('feeds', [])
    if not feeds:
        return jsonify({
            'latest': None,
            'message': 'No data available'
        })
    
    parsed_feeds = parse_feeds(feeds)
    latest = parsed_feeds[0] if parsed_feeds else None
    
    return jsonify({
        'latest': latest
    })


if __name__ == '__main__':
    # Check if configuration is available
    if not THINGSPEAK_READ_KEY or not THINGSPEAK_CHANNEL_ID:
        print("⚠️  Warning: ThingSpeak credentials not configured!")
        print("   Please set THINGSPEAK_READ_KEY and THINGSPEAK_CHANNEL_ID")
        print("   in credentials.py or as environment variables.")
        print("   The app will run but won't be able to fetch data.")
    
    # Get port from environment variable or use default 5001 (5000 is often used by AirPlay on macOS)
    port = int(os.getenv('PORT', 5001))
    
    print(f"🌐 Starting server on http://localhost:{port}")
    print(f"📊 Dashboard available at: http://localhost:{port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)

