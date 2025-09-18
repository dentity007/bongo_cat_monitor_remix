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

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument('--mode', default='normal', choices=['normal', 'messenger', 'tutor'])
parser.add_argument('--port', default=None)
args = parser.parse_args()

# Load triggers (create if missing)
triggers_file = 'triggers.json'
if os.path.exists(triggers_file):
    with open(triggers_file, 'r') as f:
        triggers = json.load(f)
else:
    triggers = {'static': [], 'dynamic': []}

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

# Keystroke listener
buffer = ""
cooldown = 0

def on_key(key):
    global buffer, cooldown
    try:
        char = key.char
        if char:
            buffer += char
            if len(buffer) > 300:
                buffer = buffer[-300:]
    except AttributeError:
        pass  # Non-char keys like space/enter

    if time.time() > cooldown and args.mode == 'normal':  # Only in normal for now
        for section in ['static', 'dynamic']:
            for t in triggers.get(section, []):
                if t['trigger'] in buffer.lower():
                    ser.write(f"MEME:{t['response']}|{t['animation']}\n".encode())
                    cooldown = time.time() + 300  # 5 min
                    buffer = ""
                    print(f"Triggered: {t['response']}")
                    break

listener = pynput.keyboard.Listener(on_press=on_key)
listener.start()

# Stub update
def update_triggers():
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_ID'),
            client_secret=os.getenv('REDDIT_SECRET'),
            user_agent='CatJAM Monitor v0.1 (by dentity007)'
        )
        
        # Test basic connectivity first
        print("🔍 Testing Reddit API connection...")
        test_sub = reddit.subreddit('test')
        test_sub.display_name  # This should work if credentials are valid
        
        print("📡 Fetching trending memes...")
        subreddit = reddit.subreddit('memes')
        trends = [post.title.lower() for post in subreddit.hot(limit=10) if post.score > 50]
        
        new_dynamic = []
        for trend in trends[:5]:
            response = f"Hot take: {trend.capitalize()}—this cat's jamming! 🐱"
            trigger_word = trend.split()[0] if trend.split() else trend
            new_dynamic.append({"trigger": trigger_word, "response": response, "animation": "meme_surprise"})
        
        triggers['dynamic'] = new_dynamic
        with open('triggers.json', 'w') as f:
            json.dump(triggers, f, indent=2)
        print(f"✅ Updated dynamic triggers with Reddit hits: {', '.join([t['trigger'] for t in new_dynamic])}")
    except Exception as e:
        print(f"❌ Reddit fetch failed: {e}")
        print("💡 Tips: Check Reddit app settings, ensure 'script' type, or try manual trigger setup")
        # Keep existing dynamic triggers if they exist, otherwise create fallback
        if not triggers.get('dynamic'):
            triggers['dynamic'] = [
                {"trigger": "lol", "response": "That joke slayed! Meow!", "animation": "meme_surprise"},
                {"trigger": "wow", "response": "Mind blown! 🐱", "animation": "meme_surprise"}
            ]
            print("🔄 Added fallback dynamic triggers")

update_triggers()  # Fetch immediately on startup

schedule.every().day.at("00:00").do(update_triggers)
update_triggers()  # Run once

print(f"Running in {args.mode} mode. Type away!")
# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)