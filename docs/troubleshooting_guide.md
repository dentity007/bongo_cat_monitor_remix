# CatJAM Monitor Troubleshooting Guide

## Local development – keep the repo clean

- Use a virtual environment for Python:  
  `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
- Install Node deps with `npm ci` (or `pnpm i --frozen-lockfile`) — but **do not commit** `node_modules/`.
- Build/cached paths are ignored via `.gitignore`: `node_modules/`, `__pycache__/`, `dist/`, `build/`, `.venv/`, `.DS_Store`, etc.
- If you accidentally track these, untrack them (they'll stay on your disk):  
  `git rm -r --cached node_modules dist build __pycache__`
- Before pushing, run `git status` — it should be clean of build or cache files.

## Common Issues and Solutions

### Python Environment Issues

#### Issue: ImportError with pynput on macOS
**Symptoms:**
```
ImportError: dlopen(/path/to/pynput/_darwin.cpython-39-darwin.so, 0x0002): Symbol not found
```

**Solutions:**
1. **Check Python Version Compatibility**
```bash
python3 --version  # Should be Python 3.9+
```

2. **Reinstall in Virtual Environment**
```bash
# Remove existing venv
rm -rf venv

# Create new venv with system Python
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd app
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Install System Dependencies (macOS)**
```bash
# Install Xcode command line tools
xcode-select --install

# Install Python development headers
brew install python@3.9
```

#### Issue: Imgflip API Connection Fails
**Symptoms:**
```
requests.exceptions.ConnectionError: Failed to establish connection
Imgflip API unavailable, using static triggers only
```

**Solutions:**
1. **Check Internet Connection**
```bash
# Test basic connectivity
ping -c 3 api.imgflip.com
```

2. **Verify API Endpoint**
   - Imgflip API doesn't require authentication
   - Check if api.imgflip.com is accessible
   - App automatically falls back to static triggers

3. **Test API Access**
```bash
cd app
python -c "import requests; print(requests.get('https://api.imgflip.com/get_memes').status_code)"
```

4. **Check Firewall/Network Restrictions**
   - Ensure outbound HTTPS connections are allowed
   - No proxy configuration needed for Imgflip

### ESP32 Hardware Issues

#### Issue: ESP32 Not Detected by Serial
**Symptoms:**
```
SerialException: could not open port /dev/ttyUSB0: [Errno 2] No such file or directory
```

**Solutions:**
1. **Check USB Connection**
```bash
# List available serial ports
ls /dev/tty*

# On macOS, might be /dev/cu.usbserial-*
ls /dev/cu.*
```

2. **Install USB Drivers**
```bash
# macOS
brew install --cask wch-ch34x-usb-serial-driver

# Linux
sudo apt-get install python3-serial
```

3. **Set Correct Permissions**
```bash
# Add user to dialout group (Linux)
sudo usermod -a -G dialout $USER

# Or use udev rules (Linux)
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"' | sudo tee /etc/udev/rules.d/99-ch340.rules
sudo udevadm control --reload-rules
```

4. **Test Serial Connection**
```bash
# Use screen to test basic connectivity
screen /dev/ttyUSB0 115200
# Type some text and press Enter
# Should see ESP32 echo back
```

#### Issue: ESP32 Display Not Working
**Symptoms:**
- TFT LCD shows no output
- ESP32 powers on but no display activity

**Solutions:**
1. **Verify Pin Connections**
   - Check TFT_CS, TFT_DC, TFT_RST pins
   - Ensure proper power connections (3.3V)
   - Verify SPI bus connections

2. **Update User_Setup.h**
```cpp
// Ensure correct display driver
#define ILI9341_DRIVER

// Set correct pins
#define TFT_CS   5
#define TFT_DC   4
#define TFT_RST  22
```

3. **Test Display Independently**
```cpp
// Add to firmware for testing
void testDisplay() {
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0);
  tft.println("Display Test");
  delay(1000);
}
```

### Trigger System Issues

#### Issue: Triggers Not Firing
**Symptoms:**
- Typing trigger words has no effect
- No serial commands sent to ESP32

**Solutions:**
1. **Check Trigger File Format**
```json
// Verify triggers.json structure
{
  "static": [
    {
      "trigger": "bullet",
      "response": "Too close for missiles...",
      "animation": "meme_surprise"
    }
  ]
}
```

2. **Test Trigger Matching**
```python
# Add debug output to main.py
def debug_trigger_check(text):
    print(f"Checking text: '{text}'")
    for trigger in triggers:
        if trigger['trigger'] in text:
            print(f"Match found: {trigger}")
            return trigger
    print("No match found")
    return None
```

3. **Verify Keyboard Monitoring**
```python
# Test pynput functionality
from pynput import keyboard

def on_press(key):
    try:
        print(f'Key pressed: {key.char}')
    except AttributeError:
        print(f'Special key pressed: {key}')

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
```

#### Issue: Dynamic Triggers Not Updating
**Symptoms:**
- Static triggers work, but only 1 trigger appears (should be 21 total: 1 static + 20 dynamic)
- No new triggers added from Imgflip API
- Triggers haven't updated recently

**Solutions:**
1. **Check Update Schedule**
   - Triggers update **daily at midnight (00:00)**
   - Triggers also update on **application startup**
   - Check system time to see when last update occurred

2. **Force Update on Startup**
   - Restart the application to trigger immediate update
   - Look for "✅ Imgflip trends loaded:" message with 20 trigger words

3. **Check Imgflip API Access**
```python
# Test Imgflip API connection
import requests

try:
    response = requests.get('https://api.imgflip.com/get_memes', timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Imgflip API working: {len(data['data']['memes'])} memes available")
        print("Top 5 trending memes:")
        for meme in data['data']['memes'][:5]:
            print(f"- {meme['name']}")
    else:
        print(f"❌ API error: {response.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

4. **Verify Trigger Count**
```python
# Check current trigger counts
import json
with open('triggers.json', 'r') as f:
    triggers = json.load(f)

static_count = len(triggers.get('static', []))
dynamic_count = len(triggers.get('dynamic', []))

print(f"Static triggers: {static_count}")
print(f"Dynamic triggers: {dynamic_count}")
print(f"Total triggers: {static_count + dynamic_count}")
print("Expected: 1 static + 20 dynamic = 21 total")
```

3. **Check Update Frequency**
```python
# Ensure update interval is reasonable
REDDIT_UPDATE_INTERVAL = 300  # 5 minutes
```

### Performance Issues

#### Issue: High CPU Usage
**Symptoms:**
- Python process uses excessive CPU
- System becomes unresponsive

**Solutions:**
1. **Optimize Keyboard Monitoring**
```python
# Use buffering instead of real-time processing
class BufferedKeyboardListener:
    def __init__(self, buffer_size=50):
        self.buffer = []
        self.buffer_size = buffer_size

    def add_key(self, key):
        self.buffer.append(key)
        if len(self.buffer) > self.buffer_size:
            self.process_buffer()
            self.buffer = []
```

2. **Implement Sleep Intervals**
```python
# Add sleep in main loop
while True:
    check_triggers()
    time.sleep(0.05)  # Reduce CPU usage
```

3. **Profile Performance**
```python
import cProfile
cProfile.run('main()', 'profile_output.prof')

# Analyze results
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(10)
```

#### Issue: Serial Communication Lag
**Symptoms:**
- Delay between typing and ESP32 response
- Commands arrive out of order

**Solutions:**
1. **Increase Serial Baud Rate**
```python
# In main.py
SERIAL_BAUD_RATE = 115200  # or 230400

# In ESP32 firmware
Serial.begin(115200);
```

2. **Implement Command Queue**
```python
class SerialQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()

    def send_command(self, command):
        self.queue.put(command)

    def _process_queue(self):
        while True:
            command = self.queue.get()
            self._send_to_serial(command)
            time.sleep(0.01)  # Small delay between commands
```

3. **Add Acknowledgment System**
```cpp
// ESP32 acknowledgment
void sendAck(String commandId) {
  Serial.println("ACK:" + commandId);
}

// Python acknowledgment handling
def wait_for_ack(command_id, timeout=1.0):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if serial.in_waiting:
            response = serial.readline().decode().strip()
            if response == f"ACK:{command_id}":
                return True
    return False
```

### Build and Compilation Issues

#### Issue: Arduino Compilation Fails
**Symptoms:**
```
error: 'TFT_eSPI' does not name a type
```

**Solutions:**
1. **Install Required Libraries**
```bash
# Using Arduino IDE
# Sketch > Include Library > Manage Libraries
# Install: TFT_eSPI, LVGL

# Using arduino-cli
arduino-cli lib install TFT_eSPI
arduino-cli lib install LVGL
```

2. **Update Library Versions**
```bash
arduino-cli lib update
```

3. **Check Board Configuration**
```bash
arduino-cli board list
arduino-cli config dump
```

#### Issue: Python Package Installation Fails
**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solutions:**
1. **Update pip and setuptools**
```bash
pip install --upgrade pip setuptools wheel
```

2. **Use Compatible Python Version**
```bash
python3.9 -m venv venv  # Use Python 3.9 specifically
```

3. **Install from Source if Needed**
```bash
pip install --no-binary :all: package-name
```

### Network and Connectivity Issues

#### Issue: Reddit API Rate Limiting
**Symptoms:**
```
prawcore.exceptions.ResponseException: received 429 HTTP response
```

**Solutions:**
1. **Implement Exponential Backoff**
```python
import time
import random

class RedditAPI:
    def __init__(self):
        self.last_request = 0
        self.min_interval = 1.0
        self.max_backoff = 60.0

    def make_request(self, func, *args, **kwargs):
        now = time.time()
        elapsed = now - self.last_request

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed + random.uniform(0, 1)
            time.sleep(sleep_time)

        try:
            result = func(*args, **kwargs)
            self.last_request = time.time()
            self.min_interval = 1.0  # Reset on success
            return result
        except prawcore.exceptions.ResponseException as e:
            if e.response.status_code == 429:
                self.min_interval = min(self.min_interval * 2, self.max_backoff)
                time.sleep(self.min_interval)
                return self.make_request(func, *args, **kwargs)
            raise
```

2. **Cache API Responses**
```python
import pickle
from pathlib import Path

class RedditCache:
    def __init__(self, cache_file='reddit_cache.pkl'):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def get(self, key, ttl=300):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key, data):
        self.cache[key] = (data, time.time())
        self._save_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
```

### Logging and Debugging

#### Enable Comprehensive Logging
```python
# In main.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler
    file_handler = RotatingFileHandler(
        'catjam.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Usage
setup_logging()
logger = logging.getLogger(__name__)
logger.info("CatJAM Monitor started")
```

#### Debug Command Line Options
```python
# Add to main.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='CatJAM Monitor')
    parser.add_argument('--mode', choices=['normal', 'debug', 'test'],
                       default='normal', help='Operation mode')
    parser.add_argument('--no-reddit', action='store_true',
                       help='Disable Reddit integration')
    parser.add_argument('--serial-port', default='/dev/ttyUSB0',
                       help='Serial port for ESP32')
    return parser.parse_args()

# Usage
args = parse_args()
if args.mode == 'debug':
    logging.getLogger().setLevel(logging.DEBUG)
```

### Getting Help

#### Debug Information Collection
```bash
# System information
uname -a
python3 --version
arduino-cli version

# Python environment
pip list
which python3

# Serial ports
ls /dev/tty* /dev/cu.*

# Log files
tail -f catjam.log
```

#### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share experiences
- **Wiki**: Check for additional documentation

#### Emergency Recovery
```bash
# Reset to clean state
rm -rf venv
rm -f .env
rm -f catjam.log
git checkout -- app/triggers.json

# Reinstall
python3 -m venv venv
source venv/bin/activate
cd app && pip install -r requirements.txt
```

---

*Troubleshooting Guide Version: 1.0.0 | Last Updated: September 17, 2025*