import serial
import pynput
import time
import json
import schedule
import argparse
import os
from textblob import TextBlob  # Optional, for later

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
    print("Triggers updated (stub—Reddit coming next!)")

schedule.every().day.at("00:00").do(update_triggers)
update_triggers()  # Run once

print(f"Running in {args.mode} mode. Type away!")
# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)