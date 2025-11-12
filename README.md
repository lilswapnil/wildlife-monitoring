# 🦉 Smart Wildlife-Monitoring System  

[![Wokwi](https://img.shields.io/badge/Wokwi-Simulate-blue?logo=wokwi)](https://wokwi.com/projects/447393208559834113)

## 📖 Overview  
The **Smart Wildlife Monitoring System** is an IoT-based solution designed to monitor animal activity using an ESP32 microcontroller and multiple sensors (PIR, ultrasonic, LDR). It intelligently detects motion, estimates animal size, determines activity periods (day/night), and uploads the data to **ThingSpeak** for visualization and analysis.  

This system helps researchers and conservationists track wildlife patterns, prevent poaching, and study animal behavior with minimal human interference.  

---

## ✨ Features  
- 🕵️ **Motion Detection** using a PIR sensor  
- 📏 **Distance Measurement** with an ultrasonic sensor  
- 💡 **Light Level Analysis** using an LDR for day/night detection  
- 🐾 **Animal Identification** (large, medium, small) with time-of-day activity classification  
- 📤 **Cloud Integration** – sends data to ThingSpeak for visualization  
- 🚨 **False Positive Filtering** using sensor fusion (distance + light)  
- 📸 **Simulated Camera Trigger** for proof-of-concept image capture  
- 🌐 **Web Dashboard** – Beautiful real-time visualization of wildlife detections  

---

## 🏗️ Hardware Setup  

| Component          | ESP32 Pin | Description |
|--------------------|-----------|-------------|
| PIR Sensor (OUT)   | GPIO 13   | Detects motion |
| Ultrasonic Trigger | GPIO 14   | Sends sound pulses |
| Ultrasonic Echo    | GPIO 12   | Receives reflected pulses |
| LDR Sensor (ADC)   | GPIO 34   | Reads light level |

---

## 🚀 Getting Started  

## 🤖 Wokwi Simulation

You can test this project without any physical hardware using the Wokwi simulator.

**[▶️ Click here to open the project in Wokwi](https://wokwi.com/projects/447393208559834113)**

The simulation is pre-configured with the ESP32, PIR sensor, ultrasonic sensor, and LDR. When you run the simulation, the ESP32 will connect to the Wokwi WiFi and start sending data to the default ThingSpeak channel.

You can interact with the sensors in the simulation:
*   **PIR Sensor:** Click on it to simulate motion.
*   **Ultrasonic Sensor:** Adjust the slider to change the distance.
*   **LDR Sensor:** Adjust the slider to change the light level.

### 1. Clone the Repository  
```bash
git clone https://github.com/lilswapnil/wildlife-monitoring.git
cd wildlife-monitoring
```

### 2. Set Up Virtual Environment

Create and activate a virtual environment to keep dependencies isolated:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

Create a `credentials.py` file from the example:

```bash
cp credentials.py.example credentials.py
```

Then edit `credentials.py` and add your ThingSpeak credentials. You can skip the WiFi credentials, as Wokwi handles the connection automatically.

**ThingSpeak Credentials:**
- **THINGSPEAK_READ_KEY**: Your ThingSpeak Read API Key (for web dashboard to fetch data)
- **THINGSPEAK_CHANNEL_ID**: Your ThingSpeak Channel ID

### 5. Run the Web Dashboard

**Important:** Make sure your virtual environment is activated before running the app!

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```bash
run.bat
```

Then open your browser and navigate to:
```
http://localhost:5001
```

The dashboard will automatically refresh to show the latest wildlife sightings from the Wokwi simulation!


---

## 🧪 Testing Without ESP32 Hardware

If you want to test the dashboard without physical ESP32 hardware, you can use the test script to simulate data:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script to send sample data
python test_send_data.py
```

This script will:
- Send 5 sample wildlife detections to ThingSpeak
- Include various animal types (Bison, Elk, Wolf, etc.)
- Include some false positives for testing
- Respect ThingSpeak's rate limits (1 update per 15 seconds)

After running the script, refresh your dashboard to see the test data!

---

## ⚙️ Configuration

The `credentials.py` file should contain all your credentials:

```python
# credentials.py
# WiFi Configuration (for ESP32)
SSID = "YOUR_WIFI_SSID"              # Your WiFi network name
PASSWORD = "YOUR_WIFI_PASSWORD"       # Your WiFi password

# ThingSpeak Configuration
THINGSPEAK_WRITE_KEY = "YOUR_THINGSPEAK_WRITE_API_KEY"  # For ESP32 to upload data

# ThingSpeak Read Configuration (for web dashboard)
THINGSPEAK_READ_KEY = "YOUR_THINGSPEAK_READ_API_KEY"    # For web app to fetch data
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"                # Your ThingSpeak channel ID
```

### 📡 Where to Find WiFi Credentials

The WiFi SSID and password are for **your local WiFi network** that the ESP32 device will connect to. Here's where to find them:

**Method 1: Check Your Current Connection**
- **macOS**: 
  - Click the WiFi icon in the menu bar → Your network name is shown at the top
  - Or: System Settings → Network → WiFi → Network Name
- **Windows**: 
  - Settings → Network & Internet → WiFi → Your network name is shown
- **Phone**: 
  - Settings → WiFi → The network you're connected to is your SSID

**Method 2: Check Your Router**
- Look for a sticker on your router/modem
- Usually shows: Network Name (SSID) and Password (WPA Key)
- Format: `SSID: YourNetworkName` and `Password: YourPassword`

**Method 3: Router Admin Panel**
- Access your router's admin page (usually `192.168.1.1` or `192.168.0.1`)
- Look for WiFi settings or Wireless settings
- Find the SSID and password there

**Important Notes:**
- The ESP32 needs to be within range of this WiFi network
- Use 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Make sure the password is correct (case-sensitive)

**Note:** The `credentials.py` file is already in `.gitignore` and will not be committed to GitHub. We use `credentials.py` instead of `secrets.py` to avoid conflicts with Python's built-in `secrets` module.

---

## 📊 Data Sent to ThingSpeak

* **Field1:** Motion detected (0/1)
* **Field2:** Distance (cm)
* **Field3:** Light level (0–4095)
* **Field4:** False positive flag (0 = real, 1 = false)
* **Field5:** Animal type (coded integer)

---

## 📂 Project Structure

```
wildlife-monitoring/
│── main.py              # ESP32 firmware (MicroPython)
│── app.py               # Flask web application
│── requirements.txt     # Python dependencies
│── credentials.py           # Credentials (ignored in git)
│── credentials.py.example  # Example credentials file
│── templates/
│   └── index.html       # Web dashboard HTML
│── static/
│   ├── css/
│   │   └── style.css    # Dashboard styles
│   └── js/
│       └── app.js       # Frontend JavaScript
│── README.md            # This file
```

---

## 🖼️ System Architecture 

<p align="center">
  <img src="assets/diagram.png" alt="System diagram: Wildlife monitoring flow" width="600">
  <br/>
  <em>High-level flow of the ESP32-based Smart Wildlife Monitoring System.</em>
</p>


---

## 🔮 Future Enhancements

* Add **real camera support** (ESP32-CAM)
* Deploy **ML models** for species recognition
* Integrate with **mobile app/dashboard** for live alerts
* Support **LoRaWAN/Edge AI** for remote monitoring

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Swapnil Bhalerao**
🔗 [GitHub Profile](https://github.com/lilswapnil)