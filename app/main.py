"""
CatJAM Monitor - Main Application

A Python application that monitors keyboard input and sends meme triggers to an ESP32
display. Features include static and dynamic triggers, Reddit integration for trending
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
import praw  # Add this import at top if not there

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
# REDDIT INTEGRATION SYSTEM
# =============================================================================

def update_triggers():
    """
    Fetch trending content from Reddit and update dynamic triggers.

    Connects to Reddit API, fetches hot posts from r/memes, and creates
    dynamic triggers based on trending content. Falls back to static
    triggers if Reddit is unavailable.
    """
    try:
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_ID'),
            client_secret=os.getenv('REDDIT_SECRET'),
            user_agent='CatJAM Monitor v0.1 (by dentity007)'
        )

        # Step 1: Test basic connectivity first
        print("🔍 Testing Reddit API connection...")
        test_sub = reddit.subreddit('test')
        test_sub.display_name  # This should work if credentials are valid

        # Step 2: Fetch trending memes from r/memes
        print("📡 Fetching trending memes...")
        subreddit = reddit.subreddit('memes')
        trends = [post.title.lower() for post in subreddit.hot(limit=10) if post.score > 50]

        # Step 3: Create dynamic triggers from trending content
        new_dynamic = []
        for trend in trends[:5]:  # Limit to top 5 trends
            response = f"Hot take: {trend.capitalize()}—this cat's jamming! 🐱"
            trigger_word = trend.split()[0] if trend.split() else trend
            new_dynamic.append({
                "trigger": trigger_word,
                "response": response,
                "animation": "meme_surprise"
            })

        # Step 4: Save updated triggers to file
        triggers['dynamic'] = new_dynamic
        with open('triggers.json', 'w') as f:
            json.dump(triggers, f, indent=2)
        print(f"✅ Updated dynamic triggers with Reddit hits: {', '.join([t['trigger'] for t in new_dynamic])}")

    except Exception as e:
        # Handle Reddit API failures gracefully
        print(f"❌ Reddit fetch failed: {e}")
        print("💡 Tips: Check Reddit app settings, ensure 'script' type, or try manual trigger setup")

        # Fallback: Keep existing dynamic triggers or create basic ones
        if not triggers.get('dynamic'):
            triggers['dynamic'] = [
                {"trigger": "lol", "response": "That joke slayed! Meow!", "animation": "meme_surprise"},
                {"trigger": "wow", "response": "Mind blown! 🐱", "animation": "meme_surprise"}
            ]
            print("🔄 Added fallback dynamic triggers")

# =============================================================================
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