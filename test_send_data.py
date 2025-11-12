#!/usr/bin/env python3
"""
Test script to simulate ESP32 sending data to ThingSpeak
This allows you to test the dashboard without physical ESP32 hardware
"""
import requests
import time
import random
from datetime import datetime

# Try to load credentials
try:
    from credentials import THINGSPEAK_WRITE_KEY
except ImportError:
    print("⚠️  Warning: credentials.py not found!")
    print("   Using default test key (may not work)")
    THINGSPEAK_WRITE_KEY = "ZB62JYMAC6Y0WI5N"

THINGSPEAK_URL = "http://api.thingspeak.com/update"

# Animal type mapping (same as main.py)
ANIMAL_MAP = {
    "Bison": 1,
    "Grizzly Bear": 2,
    "Mountain Lion": 3,
    "Elk": 4,
    "Wolf": 5,
    "Unknown": 0
}

def send_test_data(motion=1, distance=None, light_level=None, animal_type="Unknown", is_false_pos=False):
    """
    Send test data to ThingSpeak
    
    Args:
        motion: 0 or 1 (motion detected)
        distance: Distance in cm (if None, generates random)
        light_level: Light level 0-4095 (if None, generates random)
        animal_type: Animal name (if None, randomly selects)
        is_false_pos: True if false positive
    """
    # Generate random values if not provided
    if distance is None:
        if animal_type == "Unknown":
            distance = random.randint(50, 450)
        elif animal_type == "Bison" or animal_type == "Grizzly Bear":
            distance = random.randint(50, 150)
        elif animal_type == "Elk":
            distance = random.randint(151, 300)
        else:  # Wolf, Mountain Lion
            distance = random.randint(301, 450)
    
    if light_level is None:
        # Simulate different times of day
        time_of_day = random.choice(["night", "day", "dusk"])
        if time_of_day == "night":
            light_level = random.randint(0, 999)
        elif time_of_day == "day":
            light_level = random.randint(3001, 4095)
        else:  # dusk/dawn
            light_level = random.randint(1000, 3000)
    
    # Convert animal name to code
    animal_code = ANIMAL_MAP.get(animal_type, 0)
    
    # Convert boolean to 0/1
    false_positive_flag = 1 if is_false_pos else 0
    
    # Prepare data
    data = {
        "api_key": THINGSPEAK_WRITE_KEY,
        "field1": motion,
        "field2": distance,
        "field3": light_level,
        "field4": false_positive_flag,
        "field5": animal_code
    }
    
    try:
        print(f"📤 Sending: Motion={motion}, Distance={distance}cm, Light={light_level}, Animal={animal_type}, FalsePos={is_false_pos}")
        response = requests.post(THINGSPEAK_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            entry_id = response.text.strip()
            if entry_id and entry_id != "0":
                print(f"✅ Success! Entry ID: {entry_id}")
                return True
            else:
                print(f"⚠️  Response: {response.text} (may be rate limited)")
                return False
        else:
            print(f"❌ Error: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending data: {e}")
        return False

def main():
    """Main function to send test data"""
    print("🦉 Wildlife Monitoring - Test Data Sender")
    print("=" * 50)
    print(f"ThingSpeak Write Key: {THINGSPEAK_WRITE_KEY[:10]}...")
    print("=" * 50)
    print()
    
    # List of animals to simulate
    animals = ["Bison", "Grizzly Bear", "Elk", "Wolf", "Mountain Lion"]
    
    print("Sending test detections...")
    print("(ThingSpeak free accounts allow 1 update per 15 seconds)")
    print()
    
    # Send a few test detections
    for i in range(5):
        print(f"\n--- Test Detection {i+1}/5 ---")
        
        # Randomly decide if it's a false positive (20% chance)
        is_false = random.random() < 0.2
        
        if is_false:
            # False positive - unreasonable distance or wrong time
            distance = random.choice([0.5, 550])
            light_level = random.randint(3500, 4095)  # Very bright (daytime)
            animal = "Unknown"
        else:
            # Valid detection
            animal = random.choice(animals)
            distance = None  # Will be generated based on animal
            light_level = None  # Will be generated randomly
        
        success = send_test_data(
            motion=1,
            distance=distance,
            light_level=light_level,
            animal_type=animal,
            is_false_pos=is_false
        )
        
        if success:
            # Wait 16 seconds between updates (ThingSpeak free tier limit)
            if i < 4:  # Don't wait after last one
                print("⏳ Waiting 16 seconds (ThingSpeak rate limit)...")
                time.sleep(16)
        else:
            print("⚠️  Skipping wait due to error")
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("✅ Test data sending complete!")
    print("📊 Check your dashboard at http://localhost:5001")
    print("   (Refresh the page to see new data)")

if __name__ == "__main__":
    main()

