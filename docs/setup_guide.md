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
- **Reddit account** (optional, for dynamic triggers)

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

### Step 4: Reddit Integration (Optional)

#### Create Reddit App
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in details:
   - **Name**: CatJAM Monitor
   - **Type**: `script`
   - **Description**: Personal meme monitor script
   - **About URL**: (leave blank)
   - **Redirect URI**: `http://localhost:8080`

#### Configure Credentials
1. Copy the **Client ID** (under app name)
2. Copy the **Secret** (labeled as "secret")
3. Create `app/.env` file:
```env
REDDIT_ID=your_client_id_here
REDDIT_SECRET=your_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### Step 5: Test Installation

#### Test Python Environment
```bash
cd app
python --version  # Should show Python 3.9+
python -c "import praw, pynput, serial; print('✅ All imports successful')"
```

#### Test ESP32 Connection
```bash
python main.py --mode normal
# Should show "Running in normal mode. Type away!"
# If ESP32 not connected: "No ports found—plug in ESP32!"
```

#### Test Triggers
- Type "bullet" → Should trigger Top Gun response
- Type "lol" → Should trigger "That joke slayed! Meow!"

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

#### Reddit Authentication Failing
- Verify app type is "script"
- Check redirect URI is `http://localhost:8080`
- Ensure description field is filled
- Wait 5-10 minutes for Reddit to process changes

#### Virtual Environment Issues
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
- Test with `python test_reddit.py` for Reddit-specific issues

## Next Steps
1. **Customize Triggers**: Add your favorite meme triggers
2. **Test Animations**: Verify ESP32 displays animations correctly
3. **Explore Modes**: Try messenger and tutor modes
4. **Contribute**: Help improve the project!

---

*Last updated: September 17, 2025*