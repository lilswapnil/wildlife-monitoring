#!/bin/bash
# Script to find ESP32 serial port on macOS

echo "🔍 Searching for ESP32 serial ports..."
echo ""

# Method 1: List all USB serial devices
echo "USB Serial Devices:"
ls -1 /dev/tty.usb* /dev/tty.usbserial* 2>/dev/null | while read port; do
    echo "  ✅ Found: $port"
done

echo ""
echo "All Serial Ports:"
ls -1 /dev/tty.* 2>/dev/null | grep -v "Bluetooth" | while read port; do
    if [ -c "$port" ]; then
        echo "  📍 $port"
    fi
done

echo ""
echo "💡 Common ESP32 port names on macOS:"
echo "   - /dev/tty.usbserial-*"
echo "   - /dev/tty.usbmodem*"
echo "   - /dev/tty.SLAB_USBtoUART"
echo ""
echo "📝 To use a port, replace /dev/ttyUSB0 with the port name above"
echo "   Example: mpremote connect /dev/tty.usbserial-1410 cp main.py :"

