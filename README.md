# 🎵 CatJAM Monitor: Bongo Cat Remix

![CatJAM Monitor](https://via.placeholder.com/800x200?text=CatJAM+Monitor+-+Bongo+Cat+Remix)

**Animated ESP32 desk buddy with meme Easter eggs, personal messages, and typing tutor!**

Transform your desk into an interactive meme factory with this enhanced Bongo Cat monitor that responds to your typing with hilarious reactions, dynamic Reddit-powered triggers, and customizable animations.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Typing Detection** - Cat responds to your keystrokes with adorable animations
- **Meme Trigger System** - Type special words to trigger custom responses and animations
- **ESP32 Integration** - Hardware display with TFT screen for visual feedback
- **Cross-platform Support** - Works on Windows, macOS, and Linux

### 🚀 Advanced Features
- **Dynamic Reddit Triggers** - Automatically fetches trending memes from Reddit
- **Static Custom Triggers** - Pre-configured meme responses
- **Multiple Modes** - Normal, Messenger, and Tutor modes
- **Fallback System** - Continues working even when Reddit is unavailable
- **Web Dashboard** - Optional web interface for configuration
- **Serial Communication** - Robust ESP32 connectivity

### 🎨 Customization
- **Trigger Management** - JSON-based trigger configuration
- **Animation System** - Extensible animation framework
- **Theme Support** - Customizable cat appearances
- **Sound Integration** - Optional audio feedback

## 📚 Documentation

| Document | Description | Link |
|----------|-------------|------|
| **Setup Guide** | Complete installation and hardware setup | [📖 Setup Guide](docs/setup_guide.md) |
| **API Reference** | Technical documentation for developers | [🔧 API Reference](docs/api_reference.md) |
| **Development Guide** | Architecture, testing, and contribution guidelines | [👨‍💻 Development Guide](docs/development_guide.md) |
| **Troubleshooting** | Common issues and solutions | [🔍 Troubleshooting Guide](docs/troubleshooting_guide.md) |
| **Style Guide** | Coding standards and best practices | [📋 Style Guide](docs/style_guide.md) |

### Key Documentation Sections
- **[Hardware Setup](docs/setup_guide.md#hardware-setup)**: ESP32 and TFT LCD configuration
- **[Reddit Integration](docs/setup_guide.md#reddit-setup)**: API configuration and authentication
- **[Trigger System](docs/api_reference.md#trigger-system)**: How triggers work and customization
- **[ESP32 Commands](docs/api_reference.md#esp32-commands)**: Firmware communication protocol
- **[Development Workflow](docs/development_guide.md#development-workflow)**: Contributing to the project

## 🏃‍♂️ Quick Start

### Prerequisites
- **Python 3.9+** (for Reddit integration)
- **ESP32 board** with 2.4" TFT display
- **Arduino IDE** for firmware flashing
- **Reddit account** (optional, for dynamic triggers)

### 1. Clone & Setup
```bash
git clone https://github.com/dentity007/bongo_cat_monitor_remix.git
cd bongo_cat_monitor_remix
```

### 2. Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd app
pip install -r requirements.txt
```

### 3. Reddit Setup (Optional)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create new app (type: `script`)
3. Copy credentials to `app/.env`:
```env
REDDIT_ID=your_client_id
REDDIT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### 4. ESP32 Setup
1. Open `firmware/bongo_cat_monitor.ino` in Arduino IDE
2. Install required libraries (TFT_eSPI, LVGL)
3. Upload to your ESP32 board

### 5. Run the App
```bash
cd app
python main.py --mode normal
```

### 6. Test Triggers
- Type "bullet" → Top Gun reference!
- Type "lol" → "That joke slayed! Meow!"
- Type "wow" → "Mind blown! 🐱"

## 📁 Project Structure

```
bongo_cat_monitor_remix/
├── 📁 app/                          # Desktop application
│   ├── 📄 main.py                   # Main Python application
│   ├── 📄 requirements.txt          # Python dependencies
│   ├── 📄 triggers.json             # Static & dynamic triggers
│   ├── 📄 trusted_triggers.json     # Verified triggers
│   ├── 📄 test_reddit.py            # Reddit auth testing
│   ├── 📄 .env                      # Environment variables (Git-ignored)
│   ├── 📁 dashboard/                # Web dashboard (future)
│   └── 📁 venv/                     # Virtual environment
├── 📁 firmware/                     # ESP32 firmware
│   └── 📄 bongo_cat_monitor.ino     # Arduino sketch
├── 📁 animations/                   # Animation assets
├── 📁 docs/                         # Documentation
├── 📁 3d_files/                     # 3D printing files
├── 📄 README.md                     # This file
├── 📄 .gitignore                    # Git ignore rules
└── 📄 LICENSE.txt                   # MIT License
```

## 🎮 Usage Guide

### Basic Operation
1. **Start the app**: `python main.py --mode normal`
2. **Type normally**: Cat responds to your typing speed
3. **Trigger memes**: Type special words for reactions
4. **Monitor activity**: Cat shows system stats and animations

### Command Line Options
```bash
python main.py [options]

Options:
  --mode {normal,messenger,tutor}  Operation mode (default: normal)
  --port PORT                     Serial port for ESP32 (auto-detect if not specified)
  --help                          Show help message
```

### Modes
- **Normal Mode**: Standard typing monitor with meme triggers
- **Messenger Mode**: Enhanced social media style responses
- **Tutor Mode**: Typing practice with feedback

## 🔧 Configuration

### Trigger System
Triggers are stored in JSON format with support for static and dynamic types:

```json
{
  "static": [
    {
      "trigger": "bullet",
      "response": "Too close for missiles—switching to guns! Meow-ver and out.",
      "animation": "meme_surprise"
    }
  ],
  "dynamic": [
    {
      "trigger": "lol",
      "response": "That joke slayed! Meow!",
      "animation": "meme_surprise"
    }
  ]
}
```

### Environment Variables
Create `app/.env` for Reddit integration:
```env
REDDIT_ID=your_client_id
REDDIT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## 🛠️ Development

### Adding New Triggers
1. Edit `app/triggers.json`
2. Add trigger object with `trigger`, `response`, and `animation` fields
3. Restart the app or it will auto-reload on next cycle

### Custom Animations
1. Add animation files to `animations/` directory
2. Update ESP32 firmware to reference new animations
3. Map animation names in trigger configuration

### ESP32 Integration
- **Display**: 2.4" ILI9341 TFT LCD (240x320 resolution)
- **Communication**: Serial at 115200 baud
- **Commands**: `MEME:response|animation` format
- **Libraries**: TFT_eSPI, LVGL 8.x

## 📊 API Reference

### Python Classes
- **CatJAMMonitor**: Main application class
- **TriggerManager**: Handles trigger loading and matching
- **RedditIntegration**: Manages Reddit API interactions
- **SerialCommunicator**: ESP32 communication handler

### ESP32 Commands
- `MEME:text|animation` - Display meme with animation
- `STATUS:cpu|ram|wpm` - Update system status
- `MODE:normal|messenger|tutor` - Change operation mode

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request

### Areas for Contribution
- **New Animations**: Create custom cat animations
- **Additional Triggers**: Add more meme triggers
- **UI Improvements**: Enhance the web dashboard
- **Cross-platform**: Improve Windows/Linux support
- **Documentation**: Help improve docs and tutorials

### Code Standards
- Use type hints for Python functions
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test changes before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 🙏 Acknowledgments

- **Original Bongo Cat**: Created by [Vostok Labs](https://github.com/vostoklabs/bongo_cat_monitor)
- **Community Contributors**: Thanks to all who help improve this project
- **Reddit Community**: For providing endless meme inspiration

## 🆘 Troubleshooting

### Common Issues

**Reddit Authentication Failing**
```
❌ Error: received 401 HTTP response
```
**Solution**: Ensure Reddit app is configured as "script" type with redirect URI `http://localhost:8080`

**ESP32 Not Connecting**
```
No ports found—plug in ESP32!
```
**Solution**: Check USB connection and ensure correct ESP32 board is selected in Arduino IDE

**Python Dependencies Missing**
```
ModuleNotFoundError: No module named 'praw'
```
**Solution**: Run `pip install -r requirements.txt` in activated virtual environment

**Virtual Environment Issues**
```
python3: command not found
```
**Solution**: Install Python 3.9+ and recreate virtual environment

### Getting Help
- 📖 **[Full Troubleshooting Guide](docs/troubleshooting_guide.md)**: Comprehensive solutions for common issues
- 🐛 **[GitHub Issues](https://github.com/dentity007/bongo_cat_monitor_remix/issues)**: Report bugs and request help
- 💬 **[GitHub Discussions](https://github.com/dentity007/bongo_cat_monitor_remix/discussions)**: Ask questions and share experiences
- 📚 **[Documentation](docs/)**: Complete technical documentation

---

**Made with ❤️ for the Bongo Cat community**

![Demo](https://via.placeholder.com/400x200?text=CatJAM+Demo)


