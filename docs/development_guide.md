# CatJAM Monitor Development Guide

## Architecture Overview

CatJAM Monitor follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Python App     │───▶│     ESP32       │
│   (Keyboard)    │    │  (main.py)      │    │   (Firmware)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Triggers      │    │   Display       │
                       │   (JSON)        │    │   (TFT LCD)     │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Imgflip API   │
                       │   (Optional)    │
                       └─────────────────┘
```

## Core Components

### 1. Main Application (`main.py`)

#### Key Functions
- **Keyboard Monitoring**: Uses `pynput` for cross-platform input detection
- **Trigger Processing**: Matches typed text against trigger database
- **Serial Communication**: Sends commands to ESP32 via pyserial
- **Imgflip Integration**: Fetches dynamic triggers (optional)
- **Mode Management**: Handles different operation modes

#### Main Loop Structure
```python
def main():
    # Initialize components
    setup_serial()
    setup_keyboard_listener()
    load_triggers()

    # Main processing loop
    while True:
        check_triggers()
        update_imgflip_triggers()  # If enabled
        process_serial_commands()
        time.sleep(0.1)
```
```

### 2. Trigger System

#### Static Triggers
Pre-configured triggers stored in `triggers.json`:
```json
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

#### Dynamic Triggers
Imgflip-powered triggers that update automatically:
```json
{
  "dynamic": [
    {
      "trigger": "trending_word",
      "response": "Hot take: [trending content]",
      "animation": "meme_surprise",
      "source": "imgflip",
      "score": 150
    }
  ]
}
```

### 3. ESP32 Firmware

#### Command Processing
```cpp
void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command.startsWith("MEME:")) {
      // Parse and display meme
      String response = parseResponse(command);
      String animation = parseAnimation(command);
      displayMeme(response, animation);
    }
  }
}
```

#### Animation System
- Frame-based animations stored in PROGMEM
- Smooth transitions between states
- Configurable timing and effects

## Development Workflow

### Setting Up Development Environment

1. **Clone Repository**
```bash
git clone https://github.com/dentity007/bongo_cat_monitor_remix.git
cd bongo_cat_monitor_remix
```

2. **Create Development Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Setup Python Environment**
```bash
python3 -m venv venv
source venv/bin/activate
cd app && pip install -r requirements.txt
```

4. **Install Development Dependencies**
```bash
pip install pytest black flake8 mypy
```

### Code Standards

#### Python Style Guidelines
- Follow PEP 8 conventions
- Use type hints for function parameters
- Write docstrings for all public functions
- Maximum line length: 88 characters

#### Example Function
```python
def process_trigger(text: str, triggers: dict) -> Optional[dict]:
    """
    Process text input and find matching triggers.

    Args:
        text: Input text to check for triggers
        triggers: Dictionary of available triggers

    Returns:
        Trigger dictionary if match found, None otherwise
    """
    for trigger_type, trigger_list in triggers.items():
        for trigger in trigger_list:
            if trigger['trigger'].lower() in text.lower():
                return trigger
    return None
```

### Testing Strategy

#### Unit Tests
```python
# tests/test_triggers.py
import pytest
from app.trigger_manager import TriggerManager

class TestTriggerManager:
    def test_static_trigger_match(self):
        manager = TriggerManager()
        result = manager.find_match("This is a bullet test")
        assert result is not None
        assert result['trigger'] == 'bullet'

    def test_no_trigger_match(self):
        manager = TriggerManager()
        result = manager.find_match("Normal text without triggers")
        assert result is None
```

#### Integration Tests
```python
# tests/test_integration.py
def test_full_trigger_flow():
    # Test complete flow from input to ESP32 command
    monitor = CatJAMMonitor()
    monitor.process_input("bullet")
    # Verify ESP32 command was sent
    assert mock_serial.last_command == "MEME:Too close for missiles...|meme_surprise"
```

#### ESP32 Testing
```cpp
// firmware/test_commands.ino
void testMemeCommand() {
  String testCommand = "MEME:Test message|meme_surprise";
  processCommand(testCommand);
  // Verify display shows correct message
  assert(displayBuffer.contains("Test message"));
}
```

### Adding New Features

#### 1. New Trigger Type
```python
# Add to trigger_manager.py
def add_custom_trigger(self, trigger: str, response: str, animation: str, custom_field: str):
    """Add trigger with custom metadata."""
    trigger_obj = {
        'trigger': trigger,
        'response': response,
        'animation': animation,
        'custom_field': custom_field,
        'created': datetime.now().isoformat()
    }
    self.triggers['custom'].append(trigger_obj)
    self.save_triggers()
```

#### 2. New Animation
```cpp
// Add to animations.h
const uint16_t custom_animation[] PROGMEM = {
  // Animation frame data
  0x0000, 0xFFFF, 0xFFFF, 0x0000,
  // ... more frames
};

// Add to animation controller
void playCustomAnimation() {
  displayAnimation(custom_animation, sizeof(custom_animation));
}
```

#### 3. New Serial Command
```python
# Add to serial_communicator.py
def send_custom_command(self, data: dict):
    """Send custom command to ESP32."""
    command = f"CUSTOM:{json.dumps(data)}"
    self.serial.write(command.encode())
```

### Debugging Tools

#### Python Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
def debug_trigger_match(text, trigger):
    print(f"DEBUG: Checking '{text}' against '{trigger['trigger']}'")
    match = trigger['trigger'].lower() in text.lower()
    print(f"DEBUG: Match result: {match}")
    return match
```

#### ESP32 Debugging
```cpp
// Add debug output
#define DEBUG_MODE true

void debugPrint(String message) {
  if (DEBUG_MODE) {
    Serial.println("[DEBUG] " + message);
  }
}

// Usage
debugPrint("Processing command: " + command);
```

#### Serial Monitor Debugging
```bash
# Monitor ESP32 output
screen /dev/ttyUSB0 115200

# Monitor Python app output
python main.py --mode normal 2>&1 | tee debug.log
```

### Performance Optimization

#### Python Optimizations
- Use sets for fast trigger lookups
- Implement trigger caching
- Optimize string matching algorithms
- Use asyncio for concurrent operations

#### ESP32 Optimizations
- Use PROGMEM for animation data
- Implement frame buffering
- Optimize SPI communication
- Use DMA for display updates

### Deployment

#### Python Application
```bash
# Create distribution
cd app
pyinstaller --onefile --name catjam main.py

# Install system-wide
sudo cp dist/catjam /usr/local/bin/
```

#### ESP32 Firmware
```bash
# Automated build script
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/
arduino-cli upload --fqbn esp32:esp32:esp32 --port /dev/ttyUSB0 firmware/
```

### Contributing Guidelines

#### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Submit pull request with description

#### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance impact assessed
- [ ] Security implications reviewed

### Future Enhancements

#### Planned Features
- **Web Dashboard**: Real-time monitoring interface
- **Plugin System**: Extensible trigger types
- **Multi-language Support**: Internationalization
- **Cloud Sync**: Cross-device trigger synchronization
- **Advanced Analytics**: Typing pattern analysis

#### Research Areas
- **Machine Learning**: Smart trigger suggestions
- **Voice Integration**: Audio command processing
- **Gesture Recognition**: Touch screen interactions
- **Network Features**: Multi-device synchronization

---

*Development Guide Version: 1.0.0 | Last Updated: September 17, 2025*