from machine import Pin, ADC
import time
import network
import urequests
import random 



# Sensor Setup
# Connect PIR's OUT pin to GPIO13
pir = Pin(13, Pin.IN)

# Connect Ultrasonic sensor pins
trigger = Pin(14, Pin.OUT)
echo = Pin(12, Pin.IN)

# Connect LDR sensor analog output to GPIO34
analog = ADC(Pin(34))      
analog.atten(ADC.ATTN_11DB)  # Set attenuation for full voltage range reading

# Try to import credentials, fallback to hardcoded values for testing
try:
    from credentials import SSID, PASSWORD, THINGSPEAK_WRITE_KEY
    ssid = SSID
    password = PASSWORD
except ImportError:
    # Fallback values (for testing or if credentials.py is not available)
    ssid = "Wokwi-GUEST"
    password = ""
    THINGSPEAK_WRITE_KEY = "ZB62JYMAC6Y0WI5N"

# ThingSpeak config
THINGSPEAK_API_KEY = THINGSPEAK_WRITE_KEY
THINGSPEAK_URL = "http://api.thingspeak.com/update"


def connect_wifi():
    print("Connecting to WiFi...")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)
    
    # Wait for connection with timeout
    max_wait = 10
    while max_wait > 0:
        if wifi.isconnected():
            print("Connected to WiFi")
            print("IP:", wifi.ifconfig()[0])
            return True
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
    
    print("Could not connect to WiFi")
    return False

def measure_distance():
    """Get raw distance measurement from ultrasonic sensor"""
    # Send trigger pulse
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    # Ultrasonic sensor timing logic
    while echo.value() == 0: pass
    start = time.ticks_us()
    while echo.value() == 1: pass
    end = time.ticks_us()
    
    # Calculate distance
    return (time.ticks_diff(end, start) * 0.0343) / 2

def get_distance():
    """Get distance reading, with occasional simulation for demonstration"""
    
    # First, get the actual reading from ultrasonic sensor
    actual_distance = measure_distance()
    
    # Decide whether to simulate (50% chance)
    if random.random() < 0.5:
        # First decide whether to generate an animal or a false reading (80/20 split)
        if random.random() < 0.8:
            # Simulate an animal (80% of simulations)
            animal_size = random.choice(["large", "medium", "small"])
            
            if animal_size == "large":  # Bison, grizzly
                return random.randint(50, 150)
            elif animal_size == "medium":  # Wolf, elk
                return random.randint(151, 300)
            else:  # Small animals
                return random.randint(301, 450)
        else:
            # Simulate a false reading (20% of simulations)
            return random.choice([0.5, 550])
    
    # Otherwise use the actual sensor reading
    return actual_distance

def simulate_camera():
    print("Camera triggered")
    print("Processing image...")
    return "Image captured"

def is_false_positive(distance, light_level):
    """Check if a detection is likely a false positive using multiple sensors"""
    
    # Rule 1: Unreasonable distance readings
    if distance > 500 or distance < 1:
        print("False positive detected: Distance value out of reasonable range")
        return True
    
    # Rule 2: Reduced wildlife activity during peak daylight
    if light_level > 3800:  # Very bright daylight
        print("False positive detected: Most wildlife reduces activity during peak daylight hours")
        return True
        
    # No false positive detected
    return False

# --- Animal Simulation Logic ---
# List of 15 potential animals to be detected in the forest environment.
# The ID corresponds to the key in the ANIMAL_CHARACTERISTICS dictionary.
ANIMAL_LIST = [
    {"id": 1, "name": "Fox"}, {"id": 2, "name": "Badger"}, {"id": 3, "name": "Deer"},
    {"id": 4, "name": "Squirrel"}, {"id": 5, "name": "Rabbit"}, {"id": 6, "name": "Hedgehog"},
    {"id": 7, "name": "Owl"}, {"id": 8, "name": "Woodpecker"}, {"id": 9, "name": "Boar"},
    {"id": 10, "name": "Bear"}, {"id": 11, "name": "Raccoon"}, {"id": 12, "name": "Skunk"},
    {"id": 13, "name": "Lynx"}, {"id": 14, "name": "Wolf"}, {"id": 15, "name": "Moose"},
]

# This dictionary maps the animal ID to its name for easy lookup.
ANIMAL_CHARACTERISTICS = {
    1: "Fox", 2: "Badger", 3: "Deer", 4: "Squirrel", 5: "Rabbit",
    6: "Hedgehog", 7: "Owl", 8: "Woodpecker", 9: "Boar", 10: "Bear",
    11: "Raccoon", 12: "Skunk", 13: "Lynx", 14: "Wolf", 15: "Moose",
    0: "Unknown",
}

def identify_animal(distance, light_level):
    """
    Identifies an animal.
    For this simulation, it randomly selects an animal from the list if the distance is valid.
    """
    # A valid detection is considered to be within a reasonable range.
    # We ignore light_level for this simplified random simulation.
    if 5 <= distance <= 450:
        # Select a random animal from our list of 15.
        detected_animal = random.choice(ANIMAL_LIST)
        return detected_animal["id"]
    
    # If distance is out of range, it's considered an invalid or unknown detection.
    return 0 # Unknown

# Upload to ThingSpeak with all data
def upload_to_thingspeak(motion, distance, light_level, animal_id, is_false_pos):
    """
    Upload all data to ThingSpeak
    field1: Motion (0 or 1)
    field2: Distance (cm)
    field3: Light Level
    field4: False Positive (0 = real detection, 1 = false positive)
    field5: Animal ID (encoded as a number)
    """
    # Convert boolean false positive flag to 0/1
    false_positive_flag = 1 if is_false_pos else 0
    
    # Create data payload
    data = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": motion,
        "field2": distance,
        "field3": light_level,
        "field4": false_positive_flag,
        "field5": animal_id
    }
    
    try:
        print("Uploading data to ThingSpeak...")
        response = urequests.post(
            THINGSPEAK_URL,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        print("Upload response:", response.text)
        response.close()
        return True
    except Exception as e:
        print("Failed to upload:", e)
        return False

# Connect to WiFi when the program starts
if not connect_wifi():
    print("Please check your WiFi configuration")

# Main loop
while True:
    # Check PIR sensor first for motion
    motion_detected = pir.value()
    print("Motion:", "Detected" if motion_detected else "None")
    
    if motion_detected:
        # Get sensor readings
        distance = get_distance()
        print("Distance:", distance, "cm")
        
        # Only check light level when motion is detected (saves power)
        light_level = 4095 - analog.read()  # Invert for intuitive readings
        print("Light level:", light_level)
        
        # Check if detection is a false positive
        false_positive = is_false_positive(distance, light_level)
        
        # Default animal ID
        animal_id = 0
        
        # Only identify animal if not a false positive
        if not false_positive:
            # Valid detection - identify the animal
            animal_id = identify_animal(distance, light_level)
            animal_name = ANIMAL_CHARACTERISTICS.get(animal_id, "Unknown")
            print(f"Valid wildlife detection! Likely a {animal_name}")
            camera_result = simulate_camera()
            print(camera_result)
        else:
            print("Ignoring false positive detection")
        
        # Upload data to ThingSpeak
        upload_to_thingspeak(
            motion=1, 
            distance=distance, 
            light_level=light_level, 
            animal_id=animal_id,
            is_false_pos=false_positive
        )
    else:
        # Even with no motion, occasionally send data to keep the connection alive
        if random.random() < 0.1:  # 10% chance to send "no motion" updates
            upload_to_thingspeak(
                motion=0,
                distance=0,
                light_level=4095 - analog.read(),
                animal_id=0,
                is_false_pos=False
            )
    
    # Wait before next reading 
    time.sleep(15)








#speed of sound = 0.0343 cm per microsecond    

# Ultrasonic sensor timing logic:
# 1. First while loop (echo.value() == 0): Waits until the echo pin turns ON
#     program is stuck in this line as long as echo.value =0
#    This indicates the sound wave has started its return journey
# 2. We record the exact start time with time.ticks_us()
# 3. Second while loop (echo.value() == 1): Waits until the echo pin turns OFF
#    This indicates the sound wave has completely returned
# 4. We record the exact end time with time.ticks_us()
# 5. The time difference * speed of sound (0.0343 cm/μs) / 2 gives distance in cm
#    We divide by 2 because the sound travels to the object and back 


# Note on distance variations:
# Even with stationary objects, we see slight variations in distance readings (403-404 cm)
# This is normal behavior for ultrasonic sensors due to:
#  - Microsecond timing variations between measurement cycles
#  - Small environmental factors affecting sound wave propagation
#  - Normal sensor measurement noise

#LDR - its resistance changes based on the amount of light falling on it.
#darkness - high resistance
#bright light - low resistance
#because light frees electrons in the semi conductor material
#analog pin measures voltage across LDR
#ADC converts this analog voltage into a digital number[0-4095] that the ESP can understand.
#ESP32 has a built in ADC. This converts analog voltage into a digital number(0-4095)


#The ESP32 uses a 12-bit ADC, providing a resolution of 4096 distinct values (0 to 4095).


# LDR (Light Dependent Resistor) and ADC explanation:
# 1. LDR's resistance DECREASES when light intensity INCREASES
# 2. The LDR sensor module has a voltage divider circuit (LDR + fixed resistor)
# 3. This circuit converts resistance changes into voltage changes
# 4. The ESP32's ADC (Analog-to-Digital Converter) on pin 34 measures this voltage
# 5. The ADC converts the analog voltage to a digital value (0-4095)
# 6. Due to how most LDR modules are wired, readings are often inverted:
#    - Lower digital values = Brighter conditions
#    - Higher digital values = Darker conditions
# 7. To make readings more intuitive, we can invert: light_level = 4095 - analog.read()
# 8. The 4095 maximum comes from the 12-bit ADC resolution (2^12 = 4096 possible values)
# 9. For wildlife monitoring, this helps determine day/night patterns in animal behavior 


# The "Unknown" animal type (coded as 0) serves several important purposes:
# 1. Data integrity: ThingSpeak requires a value for every field in each upload. 
#    When no animal is detected (false positives or no motion), we still need 
#    a valid value to send.
# 2. Status tracking: "Unknown" provides a clear baseline in our visualization,
#    making it easier to distinguish between periods of no detection and actual
#    wildlife detection events.
