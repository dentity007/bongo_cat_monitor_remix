# CatJAM Monitor API Reference

## Python API

### Core Classes

#### `CatJAMMonitor`
Main application class that orchestrates all components.

**Initialization:**
```python
monitor = CatJAMMonitor(mode='normal', port=None)
```

**Parameters:**
- `mode` (str): Operation mode ('normal', 'messenger', 'tutor')
- `port` (str): Serial port for ESP32 (auto-detect if None)

**Methods:**
- `start()`: Begin monitoring and trigger processing
- `stop()`: Stop all monitoring and cleanup
- `add_trigger(trigger, response, animation)`: Add new trigger
- `remove_trigger(trigger)`: Remove existing trigger

#### `TriggerManager`
Handles loading, validation, and matching of triggers.

**Methods:**
- `load_triggers()`: Load triggers from JSON files
- `save_triggers()`: Save current triggers to disk
- `find_match(text)`: Find trigger matches in text
- `add_static_trigger(trigger, response, animation)`: Add static trigger
- `add_dynamic_trigger(trigger, response, animation)`: Add dynamic trigger

#### `RedditIntegration`
Manages Reddit API interactions for dynamic triggers.

**Initialization:**
```python
reddit = RedditIntegration()
```

**Methods:**
- `authenticate()`: Authenticate with Reddit API
- `fetch_trends(limit=10)`: Fetch trending posts
- `generate_triggers(trends)`: Convert trends to triggers
- `update_dynamic_triggers()`: Refresh dynamic trigger list

#### `SerialCommunicator`
Handles communication with ESP32 hardware.

**Methods:**
- `connect(port)`: Establish serial connection
- `disconnect()`: Close serial connection
- `send_command(command)`: Send command to ESP32
- `read_response()`: Read response from ESP32

### Data Structures

#### Trigger Object
```python
{
  "trigger": "word_or_phrase",
  "response": "display_text",
  "animation": "animation_name"
}
```

#### Configuration Object
```python
{
  "static_triggers": [...],
  "dynamic_triggers": [...],
  "reddit_enabled": true,
  "serial_port": "auto",
  "update_interval": 3600
}
```

## ESP32 Firmware API

### Serial Commands

#### Meme Display Command
```
MEME:response_text|animation_name
```
**Example:**
```
MEME:Too close for missiles—switching to guns! Meow-ver and out.|meme_surprise
```

#### Status Update Command
```
STATUS:cpu_usage|ram_usage|words_per_minute
```
**Example:**
```
STATUS:45|67|85
```

#### Mode Change Command
```
MODE:mode_name
```
**Example:**
```
MODE:messenger
```

### Animation System

#### Available Animations
- `idle`: Default resting animation
- `typing`: Active typing animation
- `meme_surprise`: Surprise reaction animation
- `sleep`: Sleep mode animation
- `happy`: Happy reaction animation
- `sad`: Sad reaction animation

#### Custom Animation Format
```cpp
// Animation frame data
const uint16_t animation_name[] PROGMEM = {
  // Frame 1 data
  0x0000, 0xFFFF, // pixel data
  // Frame 2 data
  0xFFFF, 0x0000,
  // ... more frames
};
```

### Configuration Constants

#### Display Settings
```cpp
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 320
#define COLOR_DEPTH 16
#define BUFFER_SIZE 2048
```

#### Serial Settings
```cpp
#define BAUD_RATE 115200
#define SERIAL_TIMEOUT 1000
#define COMMAND_BUFFER_SIZE 256
```

#### Animation Settings
```cpp
#define FRAME_RATE 30
#define ANIMATION_DELAY 100
#define TRANSITION_DURATION 500
```

## Web Dashboard API (Future)

### REST Endpoints

#### GET /api/triggers
Get all current triggers
```json
{
  "static": [...],
  "dynamic": [...],
  "last_updated": "2025-09-17T22:00:00Z"
}
```

#### POST /api/triggers
Add new trigger
```json
{
  "type": "static",
  "trigger": "new_word",
  "response": "response_text",
  "animation": "animation_name"
}
```

#### DELETE /api/triggers/{trigger_id}
Remove trigger by ID

#### GET /api/status
Get system status
```json
{
  "esp32_connected": true,
  "reddit_authenticated": false,
  "active_triggers": 5,
  "uptime": 3600
}
```

#### POST /api/test-trigger
Test trigger without ESP32
```json
{
  "trigger": "test_word",
  "response": "Test response",
  "animation": "test_animation"
}
```

### WebSocket Events

#### trigger_activated
```json
{
  "trigger": "bullet",
  "response": "Too close for missiles...",
  "timestamp": "2025-09-17T22:00:00Z"
}
```

#### system_status
```json
{
  "cpu": 45,
  "ram": 67,
  "wpm": 85,
  "esp32_status": "connected"
}
```

## Error Codes

### Python Application
- `ERR_SERIAL_CONNECTION`: Cannot connect to ESP32
- `ERR_REDDIT_AUTH`: Reddit authentication failed
- `ERR_TRIGGER_LOAD`: Cannot load trigger configuration
- `ERR_CONFIG_SAVE`: Cannot save configuration changes

### ESP32 Firmware
- `ERR_DISPLAY_INIT`: Display initialization failed
- `ERR_SERIAL_BUFFER`: Serial buffer overflow
- `ERR_ANIMATION_LOAD`: Animation data corrupted
- `ERR_MEMORY_LOW`: Insufficient memory for operation

## Rate Limits

### Reddit API
- **Authenticated requests**: 600 per 10 minutes
- **Read-only requests**: 60 per minute
- **Dynamic trigger updates**: Every 1 hour (configurable)

### Serial Communication
- **Baud rate**: 115200
- **Buffer size**: 256 bytes
- **Timeout**: 1000ms
- **Retry attempts**: 3

## File Formats

### Trigger Configuration (JSON)
```json
{
  "$schema": "https://raw.githubusercontent.com/dentity007/bongo_cat_monitor_remix/main/docs/trigger_schema.json",
  "static": [
    {
      "trigger": "string",
      "response": "string",
      "animation": "string",
      "enabled": true,
      "cooldown": 300
    }
  ],
  "dynamic": [
    {
      "trigger": "string",
      "response": "string",
      "animation": "string",
      "source": "reddit",
      "score": 150,
      "expires": "2025-09-18T00:00:00Z"
    }
  ]
}
```

### Environment Configuration (.env)
```env
# Reddit API Credentials
REDDIT_ID=your_client_id
REDDIT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
UPDATE_INTERVAL=3600

# Hardware Settings
SERIAL_PORT=auto
DISPLAY_WIDTH=240
DISPLAY_HEIGHT=320
```

---

*API Version: 1.0.0 | Last Updated: September 17, 2025*