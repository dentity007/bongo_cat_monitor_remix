# CatJAM Monitor API Reference

## Python API

### Core Modules

#### `main.py` - Application Entry Point
Main application orchestrator with resilient initialization.

**Functions:**
- `main()`: Parse arguments and start application
- `setup_logging()`: Configure application logging
- `initialize_components()`: Initialize all modules with error handling

**Command Line Arguments:**
```bash
python main.py [options]

Options:
  --mode {normal,messenger,tutor}  Operation mode (default: normal)
  --port PORT                     Serial port for ESP32 (auto-detect if not specified)
  --debug                         Enable debug logging
```

#### `engine.py` - Core Engine
BongoCatEngine class handling keyboard monitoring, serial communication, and animations.

**Class: `BongoCatEngine`**
```python
engine = BongoCatEngine(config=None)
```

**Key Methods:**
- `start_monitoring()`: Begin keyboard monitoring and ESP32 communication
- `stop_monitoring()`: Stop all monitoring threads
- `on_key_press(key)`: Handle keystroke events
- `send_animation_command(wpm, force_update=False)`: Send commands to ESP32
- `apply_config_to_arduino()`: Update ESP32 with current configuration

#### `settings.py` - Configuration Management
JSON-based settings with consent validation.

**Functions:**
- `load() -> Dict[str, Any]`: Load settings from settings.json
- `save(cfg: Dict[str, Any])`: Save settings to disk
- `is_monitoring_allowed(cfg: Dict[str, Any]) -> bool`: Check if hardware monitoring is allowed

**Settings Structure:**
```json
{
  "telemetry": {
    "hardware_monitoring_enabled": false,
    "hardware_monitoring_consented": false,
    "provider": "auto",
    "gpu_only": true
  },
  "display": {
    "show_cpu": true,
    "show_ram": true,
    "show_wpm": true,
    "show_time": true,
    "show_cpu_temp": false,
    "show_gpu_temp": false
  }
}
```

#### `sensors.py` - Hardware Monitoring
Multi-provider hardware temperature monitoring.

**Functions:**
- `read_sensors(cfg: Dict[str, Any]) -> Dict[str, Any]`: Read hardware sensors based on config
- `read_lhm_http(url: str) -> Dict[str, Any]`: Read from LibreHardwareMonitor HTTP
- `read_nvml_gpu_temp() -> Optional[float]`: Read NVIDIA GPU temperature
- `summarize_lhm(tree: Dict[str, Any]) -> Dict[str, Optional[float]]`: Parse LHM JSON response

**Supported Providers:**
- `auto`: Automatic provider detection
- `lhm_http`: LibreHardwareMonitor HTTP server
- `nvml`: NVIDIA Management Library (GPU only)

#### `resilience.py` - API Resilience Framework
Enterprise-grade resilience patterns for external API calls.

**Classes:**

**`TTLCache`** - In-memory TTL cache with disk persistence
```python
cache = TTLCache()
cache.put(key: str, value: Any)
hit, value, stale = cache.get(key: str, ttl_s: int)
```

**`CircuitBreaker`** - Circuit breaker pattern implementation
```python
breaker = CircuitBreaker(name: str, fail_threshold: int = 3, open_window_s: int = 600)
breaker.allow() -> bool  # Check if call should be attempted
breaker.record_success()  # Record successful call
breaker.record_failure()  # Record failed call
```

#### `sensors.py` - Hardware Monitoring
Multi-provider hardware temperature monitoring with consent management.

**Class: `HardwareMonitor`**
```python
monitor = HardwareMonitor(config)
```

**Key Features:**
- Consent-gated hardware access
- Multiple provider support (LibreHardwareMonitor, NVML)
- Automatic provider fallback
- Temperature data caching

**Methods:**
- `get_temperatures() -> Dict[str, float]`: Get current hardware temperatures
- `is_consent_granted() -> bool`: Check if user has granted hardware monitoring consent
- `request_consent() -> bool`: Request hardware monitoring consent from user
- `test_provider(provider_name: str) -> bool`: Test specific hardware monitoring provider

**Supported Providers:**
- `libre`: LibreHardwareMonitor HTTP server
- `nvml`: NVIDIA Management Library (NVML)

#### `resilience.py` - API Resilience Framework
Enterprise-grade API resilience with caching and circuit breaker patterns.

**Class: `TTLCache`**
```python
cache = TTLCache(ttl_seconds=300)
```

**Methods:**
- `get(key) -> Any`: Get cached value if not expired
- `set(key, value)`: Cache value with TTL
- `clear()`: Clear all cached values

**Class: `CircuitBreaker`**
```python
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
```

**Methods:**
- `call(func, *args, **kwargs)`: Execute function with circuit breaker protection
- `is_open() -> bool`: Check if circuit breaker is open
- `reset()`: Reset circuit breaker state

**Functions:**
- `resilient_json(name, url, cache_key, ttl_s, local_fallback_fn, non_blocking=True)`: Make resilient API call
- `fetch_json_with_retries(url, timeout_s=1.5, attempts=3)`: HTTP request with retries
Imgflip API integration with resilience patterns.

**Functions:**
- `get_memes(non_blocking=True) -> Tuple[Dict, Dict]`: Fetch trending memes with resilience
- `extract_template_names(resp: Dict) -> List[str]`: Extract meme names from API response

#### `gui.py` - Settings Interface
Tkinter-based GUI with hardware monitoring controls.

**Class: `SettingsGUI`**
```python
gui = SettingsGUI(config, on_config_change_callback)
```

**Key Features:**
- Hardware monitoring consent dialog
- Sensor testing interface
- Real-time configuration updates
- Provider selection and testing

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

#### Hardware Monitoring Data
```python
{
  "temperatures": {
    "cpu": 45.5,
    "gpu": 62.3,
    "memory": 38.7
  },
  "provider": "libre",
  "last_updated": "2025-09-17T22:00:00Z",
  "consent_granted": true
}
```

#### Resilience Status
```python
{
  "circuit_breaker_state": "closed",
  "cache_entries": 15,
  "last_api_call": "2025-09-17T22:00:00Z",
  "failure_count": 0
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
  "imgflip_connected": true,
  "active_triggers": 21,
  "static_triggers": 1,
  "dynamic_triggers": 20,
  "last_update": "2025-09-17T00:00:00Z",
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
- `ERR_IMGFLIP_API`: Imgflip API request failed
- `ERR_TRIGGER_LOAD`: Cannot load trigger configuration
- `ERR_CONFIG_SAVE`: Cannot save configuration changes
- `ERR_HARDWARE_MONITORING`: Hardware monitoring initialization failed
- `ERR_CONSENT_DENIED`: User denied hardware monitoring consent
- `ERR_PROVIDER_UNAVAILABLE`: Hardware monitoring provider not available
- `ERR_CIRCUIT_BREAKER_OPEN`: API circuit breaker is open
- `ERR_CACHE_MISS`: Required cached data not available

### ESP32 Firmware
- `ERR_DISPLAY_INIT`: Display initialization failed
- `ERR_SERIAL_BUFFER`: Serial buffer overflow
- `ERR_ANIMATION_LOAD`: Animation data corrupted
- `ERR_MEMORY_LOW`: Insufficient memory for operation

## Rate Limits

### Imgflip API
- **Requests**: No rate limiting (free API)
- **Reliability**: 99.9% uptime
- **Dynamic trigger updates**: Daily at midnight (00:00)
- **Startup updates**: Triggers refresh on application launch
- **Fallback**: Automatic fallback to static triggers on API failure

### Hardware Monitoring
- **LibreHardwareMonitor**: Local HTTP server, no rate limiting
- **NVML**: GPU polling interval minimum 1 second
- **Temperature updates**: Configurable interval (default 5 seconds)
- **Consent checks**: Performed once per session

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
      "source": "imgflip",
      "score": 150,
      "expires": "2025-09-18T00:00:00Z"
    }
  ]
}
```

### Environment Configuration (.env)
```env
# Optional: For future API integrations
# IMGFLIP_API_KEY=your_api_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
UPDATE_INTERVAL=3600

# Hardware Monitoring Settings
HARDWARE_MONITORING_ENABLED=false
LIBRE_HARDWARE_MONITOR_URL=http://localhost:8085
NVML_ENABLED=true
TEMPERATURE_THRESHOLD=80.0
HARDWARE_UPDATE_INTERVAL=5

# Resilience Settings
CACHE_TTL_SECONDS=300
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
API_TIMEOUT_SECONDS=1.5
MAX_API_RETRIES=3

# Hardware Settings
SERIAL_PORT=auto
DISPLAY_WIDTH=240
DISPLAY_HEIGHT=320
```
```

---

*API Version: 1.1.0 | Last Updated: September 17, 2025*