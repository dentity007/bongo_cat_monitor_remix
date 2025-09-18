#!/usr/bin/env python3
"""
Direct ESP32 Test Script

A standalone test script for directly communicating with the ESP32 hardware.
This script bypasses the main application and sends test commands to verify
that the ESP32 display and serial communication are working correctly.

Usage:
    python direct_test.py

Requirements:
    - ESP32 connected to COM9 (Windows) or appropriate serial port
    - ESP32 firmware uploaded and running
    - pyserial and psutil packages installed

Author: dentity007
Version: 1.0.0
Date: September 2025
"""

import serial
import time
import psutil

def test_direct_esp32():
    """
    Main test function that connects to ESP32 and sends test commands.

    This function:
    1. Establishes serial connection to ESP32
    2. Gathers current system statistics
    3. Sends test commands to ESP32
    4. Checks for responses
    5. Provides user feedback on test results
    """
    print("🔧 Direct ESP32 Test")
    print("=" * 40)

    try:
        # =====================================================================
        # STEP 1: Establish Serial Connection
        # =====================================================================
        print("🔌 Connecting to COM9...")
        ser = serial.Serial('COM9', 115200, timeout=1)
        print("✅ Connected to COM9!")

        # =====================================================================
        # STEP 2: Gather System Statistics
        # =====================================================================
        print("📊 Gathering system stats...")
        cpu = int(psutil.cpu_percent(interval=1))  # Get CPU usage over 1 second
        ram = int(psutil.virtual_memory().percent)  # Get RAM usage percentage
        current_time = time.strftime("%H:%M")  # Get current time in HH:MM format

        print(f"📊 System Stats: CPU={cpu}%, RAM={ram}%, Time={current_time}")

        # =====================================================================
        # STEP 3: Prepare Test Commands
        # =====================================================================
        # Define test commands to send to ESP32
        commands = [
            f'CPU:{cpu}',      # Send current CPU usage
            f'RAM:{ram}',      # Send current RAM usage
            f'WPM:25',         # Send test typing speed (words per minute)
            f'TIME:{current_time}',  # Send current time
            'ANIM:2'           # Trigger animation change
        ]

        # =====================================================================
        # STEP 4: Send Commands to ESP32
        # =====================================================================
        print("\n📤 Sending commands:")
        for cmd in commands:
            full_cmd = f'{cmd}\n'  # Add newline terminator
            ser.write(full_cmd.encode())  # Send as bytes
            print(f"  Sent: {cmd}")
            time.sleep(0.1)  # Small delay between commands to prevent overflow

        # =====================================================================
        # STEP 5: Wait and Check for Response
        # =====================================================================
        print("\n⏱️ Waiting 3 seconds for ESP32 to process...")
        time.sleep(3)

        # Check if ESP32 sent any response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"📥 ESP32 Response: {repr(response)}")
        else:
            print("📥 No response from ESP32 (this is normal)")

        # =====================================================================
        # STEP 6: Cleanup and User Feedback
        # =====================================================================
        ser.close()  # Close serial connection
        print("✅ Test completed!")
        print("\n💡 Check your ESP32 screen - you should see:")
        print(f"   CPU: {cpu}%")
        print(f"   RAM: {ram}%")
        print(f"   WPM: 25")
        print(f"   Time: {current_time}")
        print("   Animation should change!")

    except Exception as e:
        # =====================================================================
        # ERROR HANDLING
        # =====================================================================
        print(f"❌ Test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Check if ESP32 is connected to COM9")
        print("   - Verify ESP32 firmware is uploaded")
        print("   - Try different serial port if COM9 doesn't work")
        print("   - Check USB drivers are installed")

# =====================================================================
# MAIN EXECUTION
# =====================================================================
if __name__ == "__main__":
    test_direct_esp32()