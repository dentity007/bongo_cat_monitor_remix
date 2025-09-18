"""
CatJAM Monitor - Main Application

A Python application that monitors keyboard input and sends meme triggers to an ESP32
display. Features include static and dynamic triggers, Imgflip API integration for trending
content, and real-time serial communication with hardware.

Author: dentity007
Version: 1.0.0
Date: September 2025
"""

import serial
import pynput
import time
import json
import schedule
import argparse
import os
from textblob import TextBlob  # Optional, for later
from dotenv import load_dotenv
load_dotenv()  # Loads .env
import requests  # For Imgflip API

# =============================================================================
# COMMAND LINE ARGUMENT PARSING
# =============================================================================

# Parse args
parser = argparse.ArgumentParser(description='CatJAM Monitor - ESP32 Meme Display')
parser.add_argument('--mode', default='normal', choices=['normal', 'messenger', 'tutor'],
                   help='Operation mode (default: normal)')
parser.add_argument('--port', default=None,
                   help='Serial port for ESP32 (auto-detect if not specified)')
args = parser.parse_args()

# =============================================================================
# TRIGGER SYSTEM INITIALIZATION
# =============================================================================

# Load triggers (create if missing)
triggers_file = 'triggers.json'
if os.path.exists(triggers_file):
    with open(triggers_file, 'r') as f:
        triggers = json.load(f)
else:
    triggers = {'static': [], 'dynamic': []}

# =============================================================================
# SERIAL COMMUNICATION SETUP
# =============================================================================

# Simple serial setup
if args.port:
    ser = serial.Serial(args.port, 115200)
else:
    # Auto-detect ports
    import serial.tools.list_ports
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if ports:
        ser = serial.Serial(ports[0], 115200)  # Assume first is ESP32
    else:
        print("No ports found—plug in ESP32!")
        exit(1)

# =============================================================================
# KEYBOARD MONITORING SYSTEM
# =============================================================================

# Keystroke listener
buffer = ""  # Stores recent keystrokes for trigger matching
cooldown = 0  # Prevents spam triggering

def on_key(key):
    """
    Handle keyboard input events.

    Processes each keystroke, maintains a rolling buffer of recent input,
    and checks for trigger words when in normal mode.

    Args:
        key: pynput Key object representing the pressed key
    """
    global buffer, cooldown
    try:
        char = key.char
        if char:
            buffer += char
            # Keep buffer size manageable to avoid memory issues
            if len(buffer) > 300:
                buffer = buffer[-300:]  # Keep last 300 characters
    except AttributeError:
        pass  # Non-char keys like space/enter don't add to buffer

    # Check for triggers only if cooldown has expired and in normal mode
    if time.time() > cooldown and args.mode == 'normal':  # Only in normal for now
        for section in ['static', 'dynamic']:
            for t in triggers.get(section, []):
                # Case-insensitive trigger matching
                if t['trigger'] in buffer.lower():
                    # Send meme command to ESP32
                    ser.write(f"MEME:{t['response']}|{t['animation']}\n".encode())
                    cooldown = time.time() + 300  # 5 minute cooldown
                    buffer = ""  # Clear buffer after trigger
                    print(f"Triggered: {t['response']}")
                    break

# Start keyboard listener
listener = pynput.keyboard.Listener(on_press=on_key)
listener.start()

# =============================================================================
# IMGFLIP MEME API INTEGRATION (FAST!)
# =============================================================================

def update_triggers():
    """
    Fetch trending memes from Imgflip API and update dynamic triggers.

    Uses Imgflip's free API to get classic and trending memes without authentication.
    Much faster than Reddit API - no auth, single HTTP request.
    """
    try:
        print("🚀 Fetching memes from Imgflip...")

        # Single fast HTTP request to Imgflip (no auth needed!)
        response = requests.get("https://api.imgflip.com/get_memes", timeout=5)

        if response.status_code == 200:
            data = response.json()['data']['memes']

            # Create dynamic triggers from top memes (super fast!)
            new_dynamic = []
            for meme in data[:10]:  # Get top 10 memes
                # Use first word of meme name as trigger
                trigger_word = meme['name'].lower().split()[0]
                # Create fun response with meme name
                response_msg = f"Viral: {meme['name']}—cat's got the meme! 😂"
                new_dynamic.append({
                    "trigger": trigger_word,
                    "response": response_msg,
                    "animation": "meme_surprise"
                })

            # Update triggers and save to file
            triggers['dynamic'] = new_dynamic
            with open('triggers.json', 'w') as f:
                json.dump(triggers, f, indent=2)

            print(f"✅ Imgflip trends loaded: {', '.join([t['trigger'] for t in new_dynamic])}")
        else:
            print(f"❌ Imgflip API error: HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        print("⏰ Imgflip request timed out - using cached triggers")
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error: {e}")
    except Exception as e:
        print(f"❌ Fetch error: {e}")

        # Fallback: Keep existing dynamic triggers or create basic ones
        if not triggers.get('dynamic'):
            triggers['dynamic'] = [
                {"trigger": "lol", "response": "That joke slayed! Meow!", "animation": "meme_surprise"},
                {"trigger": "wow", "response": "Mind blown! 🐱", "animation": "meme_surprise"}
            ]
            print("🔄 Using fallback triggers")# =============================================================================
# SCHEDULER SETUP
# =============================================================================

# Initial trigger update on startup
update_triggers()

# Schedule daily updates at midnight
schedule.every().day.at("00:00").do(update_triggers)

# =============================================================================
# MAIN APPLICATION LOOP
# =============================================================================

print(f"Running in {args.mode} mode. Type away!")
# Main loop
while True:
    schedule.run_pending()  # Check for scheduled tasks
    time.sleep(1)  # Prevent CPU overuse