from machine import Pin, ADC
import time
import network
import urequests
import random
import config

# --- Sensor Initialization ---
pir = Pin(config.PIR_PIN, Pin.IN)
trigger = Pin(config.ULTRASONIC_TRIGGER_PIN, Pin.OUT)
echo = Pin(config.ULTRASONIC_ECHO_PIN, Pin.IN)
analog = ADC(Pin(config.LDR_PIN))
analog.atten(ADC.ATTN_11DB)

# --- Credentials & Configuration ---
try:
    from credentials import SSID, PASSWORD, THINGSPEAK_WRITE_KEY
    wifi_ssid = SSID
    wifi_password = PASSWORD
    thingspeak_api_key = THINGSPEAK_WRITE_KEY
except ImportError:
    print("Warning: credentials.py not found. Using fallback values from config.py.")
    wifi_ssid = config.WIFI_SSID
    wifi_password = config.WIFI_PASSWORD
    thingspeak_api_key = config.THINGSPEAK_API_KEY

# --- Network Functions ---
def connect_wifi():
    """Establishes a connection to the configured WiFi network."""
    print(f"Connecting to WiFi network: {wifi_ssid}")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(wifi_ssid, wifi_password)
    
    max_wait = 10
    while max_wait > 0 and not wifi.isconnected():
        print("Waiting for connection...")
        time.sleep(1)
        max_wait -= 1
    
    if wifi.isconnected():
        print("Connected to WiFi. IP:", wifi.ifconfig()[0])
        return True
    else:
        print("Failed to connect to WiFi.")
        return False

# --- Sensor Reading Functions ---
def measure_distance_raw():
    """Measures distance using the ultrasonic sensor. Returns distance in cm."""
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    # Wait for the echo pulse to start and end
    while echo.value() == 0: pass
    start = time.ticks_us()
    while echo.value() == 1: pass
    end = time.ticks_us()
    
    # Calculate distance based on sound travel time
    return (time.ticks_diff(end, start) * config.SPEED_OF_SOUND) / 2

def get_simulated_distance():
    """Generates a simulated distance reading for demonstration purposes."""
    if random.random() < config.SIMULATED_ANIMAL_PROBABILITY:
        # 80% chance to simulate a valid animal distance
        return random.randint(config.MIN_VALID_DISTANCE, config.MAX_VALID_DISTANCE)
    else:
        # 20% chance to simulate a false reading (too close or too far)
        return random.choice([0.5, 550])

def get_distance():
    """
    Returns a distance reading. Uses a real sensor reading or a simulated one
    based on the configured probability.
    """
    if random.random() < config.SIMULATION_PROBABILITY:
        return get_simulated_distance()
    return measure_distance_raw()

def get_light_level():
    """Reads the LDR and returns an inverted, more intuitive light level."""
    # Invert reading: 0 = brightest, 4095 = darkest
    return 4095 - analog.read()

# --- Logic Functions ---
def is_false_positive(distance, light_level):
    """
    Determines if a detection is likely a false positive based on sensor data.
    """
    if not (config.FALSE_POSITIVE_MIN_DISTANCE < distance < config.FALSE_POSITIVE_MAX_DISTANCE):
        print("Info: False positive suspected (distance out of range).")
        return True
    
    if light_level < config.PEAK_DAYLIGHT_THRESHOLD: # Very bright
        print("Info: False positive suspected (peak daylight).")
        return True
        
    return False

def identify_animal(distance, light_level):
    """
    Identifies an animal based on distance and light level.
    This enhanced simulation considers the animal's typical activity time.
    """
    if not (config.MIN_VALID_DISTANCE <= distance <= config.MAX_VALID_DISTANCE):
        return 0 # Unknown/invalid

    # Determine current environment (day, night, or dusk/dawn)
    if light_level > config.DARK_THRESHOLD:
        time_of_day = 'nocturnal'
    elif light_level < config.BRIGHT_THRESHOLD:
        time_of_day = 'diurnal'
    else:
        time_of_day = 'crepuscular'

    # Filter animals that are active at this time_of_day
    possible_animals = [
        animal_id for animal_id, props in config.ANIMAL_CHARACTERISTICS.items()
        if props['activity'] == time_of_day or props['activity'] == 'any'
    ]
    
    if not possible_animals:
        return 0 # No suitable animal found, return Unknown

    # Randomly select from the filtered list
    return random.choice(possible_animals)

def upload_to_thingspeak(payload):
    """Uploads a data payload to ThingSpeak."""
    payload['api_key'] = thingspeak_api_key
    
    try:
        print(f"Uploading to ThingSpeak: {payload}")
        response = urequests.post(
            config.THINGSPEAK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        print("Upload response code:", response.status_code)
        response.close()
        return True
    except Exception as e:
        print(f"Failed to upload to ThingSpeak: {e}")
        return False

# --- Main Execution ---
if not connect_wifi():
    print("Halting execution. Cannot connect to WiFi.")
    # In a real device, you might want to retry or enter a low-power mode.
    while True: time.sleep(60)

print("\n--- Wildlife Monitoring System Activated ---")
while True:
    motion_detected = pir.value()
    
    if motion_detected:
        print("\nMotion Detected!")
        
        # Gather all sensor data
        distance = get_distance()
        light_level = get_light_level()
        print(f"Sensor Data -> Distance: {distance:.1f} cm, Light: {light_level}")
        
        # Analyze data
        false_positive = is_false_positive(distance, light_level)
        animal_id = 0 if false_positive else identify_animal(distance, light_level)
        
        if not false_positive and animal_id != 0:
            animal_name = config.ANIMAL_CHARACTERISTICS.get(animal_id, {}).get("name", "Unknown")
            print(f"Analysis -> Valid detection: {animal_name}")
        else:
            print("Analysis -> Invalid or false positive detection.")

        # Prepare and upload data
        upload_payload = {
            "field1": 1,
            "field2": distance,
            "field3": light_level,
            "field4": 1 if false_positive else 0,
            "field5": animal_id
        }
        upload_to_thingspeak(upload_payload)
        
    else:
        # No motion, occasionally send a keep-alive signal
        if random.random() < config.NO_MOTION_UPDATE_PROBABILITY:
            print("\nNo motion detected. Sending keep-alive status.")
            upload_payload = {
                "field1": 0,
                "field2": 0,
                "field3": get_light_level(),
                "field4": 0,
                "field5": 0
            }
            upload_to_thingspeak(upload_payload)

    # Wait before the next cycle
    print("\nWaiting for next cycle...")
    time.sleep(15)