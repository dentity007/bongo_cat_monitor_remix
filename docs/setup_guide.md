# CatJAM Monitor Setup Guide

## Prerequisites

Before setting up CatJAM Monitor, ensure you have the following:

### Hardware Requirements
- **ESP32 Development Board** with 2.4" TFT display
  - Recommended: ESP32-2432S028R (includes integrated TFT)
  - Display: ILI9341 TFT LCD (240x320 resolution)
  - Interface: SPI with touch capability

### Software Requirements
- **Python 3.9 or higher**
- **Arduino IDE** (version 1.8.19 or later)
- **Git** for version control
- **Internet connection** (for dynamic Imgflip triggers)

### System Compatibility
- ✅ **macOS** (primary development platform)
- ✅ **Windows** 10/11
- ✅ **Linux** (Ubuntu, Debian, etc.)

## Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/dentity007/bongo_cat_monitor_remix.git
cd bongo_cat_monitor_remix
```

### Step 2: Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
cd app
pip install -r requirements.txt
```

### Step 3: ESP32 Firmware Setup

#### Install Arduino IDE
1. Download from [arduino.cc](https://www.arduino.cc/en/software)
2. Install ESP32 board support:
   - Open Arduino IDE
   - Go to `File > Preferences`
   - Add board URL: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Go to `Tools > Board > Boards Manager`
   - Search for "ESP32" and install

#### Install Required Libraries
1. Open Arduino IDE
2. Go to `Sketch > Include Library > Manage Libraries`
3. Install:
   - **TFT_eSPI** by Bodmer
   - **LVGL** by kisvegabor (version 8.x)

#### Configure TFT_eSPI
1. Navigate to Arduino libraries folder
2. Open `TFT_eSPI/User_Setup.h`
3. Uncomment and configure for your ESP32 board:
```cpp
#define ESP32_2432S028R  // For recommended board
#define TFT_MOSI 23
#define TFT_MISO 19
#define TFT_SCLK 18
#define TFT_CS 15
#define TFT_DC 2
#define TFT_RST 4
```

#### Upload Firmware
1. Open `firmware/bongo_cat_monitor.ino` in Arduino IDE
2. Select your ESP32 board from `Tools > Board`
3. Select correct port from `Tools > Port`
4. Click `Upload` button

### Step 4: Imgflip Integration (Optional)

#### No Setup Required!
The Imgflip API integration requires **no authentication** and works out of the box:

1. **Automatic Setup** - The app automatically connects to Imgflip API on startup
2. **No Credentials Needed** - Free API with no rate limits or authentication
3. **Fast Loading** - 30x faster than Reddit (loads in under 1 second)
4. **Reliable Service** - 99.9% uptime with robust fallback system

#### Dynamic Triggers Available
Once running, you'll have access to **20 trending memes** that update **daily at midnight**:
- `drake` → Drake Hotline Bling reaction
- `bernie` → Bernie Sanders "I am once again asking"
- `epic` → Epic Handshake celebration
- `disaster` → Disaster Girl meme
- `gru's` → Gru's Plan meme
- `batman` → Batman Slapping Robin meme
- And 14 more viral memes updated automatically!

**Note**: Triggers update daily at midnight and on application startup. If Imgflip API is unavailable, the app continues working with static triggers only.

### Step 5: Test Installation

#### Test Python Environment
```bash
cd app
python --version  # Should show Python 3.9+
python -c "import requests, pynput, serial; print('✅ All imports successful')"
```

#### Test ESP32 Connection
```bash
python main.py --mode normal
# Should show "Running in normal mode. Type away!"
# If ESP32 not connected: "No ports found—plug in ESP32!"
```

#### Test Triggers
- Type "bullet" → Should trigger Top Gun response
- Type "drake" → Should trigger Drake Hotline Bling meme
- Type "bernie" → Should trigger Bernie Sanders meme
- Type "epic" → Should trigger Epic Handshake meme
- Type "batman" → Should trigger Batman Slapping Robin meme
- Type "gru's" → Should trigger Gru's Plan meme
- And 15 more dynamic triggers updated daily!

## Configuration Options

### Trigger Configuration
Edit `app/triggers.json` to customize triggers:

```json
{
  "static": [
    {
      "trigger": "your_word",
      "response": "Your custom response",
      "animation": "meme_surprise"
    }
  ],
  "dynamic": []
}
```

### Serial Port Configuration
If auto-detection fails, specify port manually:
```bash
python main.py --port /dev/ttyUSB0  # Linux
python main.py --port COM3          # Windows
python main.py --port /dev/tty.usbserial-0001  # macOS
```

## Troubleshooting

### Common Issues

#### Python Version Issues
```bash
python3 --version  # Check version
python3 -m venv venv  # Recreate with Python 3
```

#### ESP32 Not Detected
- Check USB cable connection
- Try different USB port
- Verify ESP32 board selection in Arduino IDE
- Check device manager (Windows) or `ls /dev/tty*` (macOS/Linux)

#### Imgflip API Issues
- **No authentication required** - API works without credentials
- **Check internet connection** - Required for dynamic triggers
- **Fallback mode** - App continues with static triggers if API fails
- **Rate limiting** - Extremely rare, but app handles it gracefully

### Step 5: Hardware Temperature Monitoring (Optional - Windows Only)

#### Prerequisites
- **Windows 10/11** (required for hardware monitoring)
- **Administrator privileges** (for LibreHardwareMonitor setup)

#### LibreHardwareMonitor Setup
1. **Download LibreHardwareMonitor**
   - Visit: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases
   - Download latest release (LibreHardwareMonitor-net472.zip)

2. **Extract and Configure**
   - Extract to a permanent location (e.g., `C:\Program Files\LibreHardwareMonitor`)
   - Run `LibreHardwareMonitor.exe` as Administrator
   - Go to `Options > Start Minimized`
   - Go to `Options > Start with Windows`
   - Go to `Options > Remote Web Server`
   - Set port to `8085` and enable the web server

3. **Verify Installation**
   - Open browser to `http://localhost:8085`
   - You should see JSON data with hardware temperatures

#### Application Configuration
1. **Enable Hardware Monitoring**
   - Run the application
   - Open settings GUI from system tray
   - Check "Enable Hardware Monitoring"
   - Grant consent when prompted
   - Select preferred provider (LibreHardwareMonitor recommended)

2. **Test Temperature Display**
   - Type to trigger cat animations
   - Temperatures should appear on ESP32 display
   - Check console for "Hardware monitoring active" message

#### Troubleshooting Hardware Monitoring
- **No temperatures displayed**: Verify LibreHardwareMonitor is running and web server enabled
- **Connection refused**: Check firewall settings and port 8085 availability
- **NVML fallback**: If LibreHardwareMonitor fails, app automatically tries NVML for NVIDIA GPUs
- **Consent required**: Hardware monitoring requires explicit user consent before enabling
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help
- Check [Issues](https://github.com/dentity007/bongo_cat_monitor_remix/issues) for common problems
- Review [README.md](README.md) for detailed documentation
- Test with `python main.py --mode normal` to verify Imgflip integration

## Next Steps
1. **Customize Triggers**: Add your favorite meme triggers
2. **Test Animations**: Verify ESP32 displays animations correctly
3. **Explore Modes**: Try messenger and tutor modes
4. **Contribute**: Help improve the project!

---

*Last updated: September 17, 2025*