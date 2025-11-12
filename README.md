# 🦉 Smart Wildlife Monitoring System  

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

### Wokwi Link: https://wokwi.com/projects/447393208559834113

### 1. Clone the Repository  
```bash
git clone https://github.com/lilswapnil/Smart-Wildlife-Monitoring-System.git
cd Smart-Wildlife-Monitoring-System
````

### 2. Flash MicroPython to ESP32

Make sure your ESP32 has MicroPython installed:

```bash
esptool.py --chip esp32 erase_flash
esptool.py --chip esp32 write_flash -z 0x1000 esp32-idf4-20230426-v1.20.0.bin
```

### 3. Set Up Virtual Environment (Recommended)

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

### 4. Install Requirements

```bash
pip install -r requirements.txt
```

**Note:** Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt) before installing packages.

### 5. Configure Secrets

Create a `credentials.py` file from the example:

```bash
cp credentials.py.example credentials.py
```

Then edit `credentials.py` and add your credentials:

**WiFi Credentials (for ESP32 device):**
- **SSID**: The name of your WiFi network (the network name you see when connecting devices)
- **PASSWORD**: The password for your WiFi network
  - *Where to find these:* 
    - On macOS: System Preferences → Network → WiFi → Network Name (SSID)
    - On Windows: Settings → Network & Internet → WiFi → Network name
    - On your router: Usually printed on a sticker on the router
    - Check your phone/computer's WiFi settings to see the network name

**ThingSpeak Credentials:**
- **THINGSPEAK_WRITE_KEY**: Your ThingSpeak Write API Key (for ESP32 to upload data)
- **THINGSPEAK_READ_KEY**: Your ThingSpeak Read API Key (for web dashboard to fetch data)
- **THINGSPEAK_CHANNEL_ID**: Your ThingSpeak Channel ID
  - *Where to get these:* 
    - Sign up at [ThingSpeak.com](https://thingspeak.com)
    - Create a new channel
    - Go to API Keys tab to get your keys
    - Channel ID is shown on your channel page

### 6. Upload Code to ESP32

**Option A: Using mpremote (Recommended)**

**Step 1: Find your ESP32's serial port**

**On macOS:**
```bash
# Run the helper script to find ports
./find_esp32_port.sh

# Or manually check:
ls /dev/tty.usb* /dev/tty.usbserial* /dev/tty.SLAB_USBtoUART 2>/dev/null
```

Common macOS port names:
- `/dev/tty.usbserial-*` (most common)
- `/dev/tty.usbmodem*`
- `/dev/tty.SLAB_USBtoUART` (if using CP2102 USB-to-Serial chip)

**On Linux:**
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

**On Windows:**
Check Device Manager → Ports (COM & LPT) → Usually `COM3`, `COM4`, etc.

**Step 2: Upload and run**

Replace `PORT_NAME` with your actual port from Step 1:

```bash
# Upload main.py to ESP32
mpremote connect PORT_NAME cp main.py :

# Run the code
mpremote connect PORT_NAME run main.py
```

**Example for macOS:**
```bash
mpremote connect /dev/tty.usbserial-1410 cp main.py :
mpremote connect /dev/tty.usbserial-1410 run main.py
```

**Troubleshooting:**
- **"Port not found"**: Make sure ESP32 is connected via USB and drivers are installed
- **"Port in use"**: Close other programs using the port (Thonny, Arduino IDE, etc.)
- **"Permission denied"**: On Linux, you may need to add your user to the `dialout` group

**Option B: Using Thonny IDE (Easiest for Beginners)**

1. Install [Thonny IDE](https://thonny.org/)
2. Connect your ESP32 via USB cable
3. Open Thonny IDE
4. Go to: **Tools → Options → Interpreter**
5. Select: **MicroPython (ESP32)** from the dropdown
6. Thonny will auto-detect your ESP32 port
7. Open `main.py` in Thonny
8. Click **Run** (F5) or click the green play button
9. The code will upload and run automatically!

**Advantages of Thonny:**
- Auto-detects ESP32 port (no need to find it manually)
- Built-in file manager to upload files
- REPL (interactive console) to debug
- No command line needed

**Option C: Test Without Hardware (Simulation)**
If you don't have ESP32 hardware yet, you can test the dashboard by sending simulated data:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the test script
python test_send_data.py
```
This will send sample wildlife detection data to ThingSpeak so you can test the dashboard.

### 7. Run the Web Dashboard

**Option 1: Using the helper script (Easiest)**

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```bash
run.bat
```

**Option 2: Manual activation**

**Important:** Make sure your virtual environment is activated before running the app!

**On macOS/Linux:**
```bash
source venv/bin/activate
python app.py
```

**On Windows:**
```bash
venv\Scripts\activate
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5001
```

**Note:** The app uses port 5001 by default to avoid conflicts with macOS AirPlay Receiver (which uses port 5000). You can change the port by setting the `PORT` environment variable:
```bash
PORT=8080 python app.py
```

The dashboard will automatically refresh every 30 seconds to show the latest wildlife detections!

**To deactivate the virtual environment when done:**
```bash
deactivate
```

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