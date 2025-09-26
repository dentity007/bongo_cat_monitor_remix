# 🖥️ Bongo Cat Desktop Application

The companion Windows application that monitors your typing and system stats, then sends this data to your ESP32 Bongo Cat display.

## 📁 Application Structure

- **`main.py`** - Application entry point with resilient initialization
- **`engine.py`** - Core functionality (keyboard monitoring, system stats, serial communication)
- **`gui.py`** - Settings interface with hardware monitoring UI and consent dialogs
- **`tray.py`** - System tray integration and menu
- **`settings.py`** - JSON-based configuration with consent validation and provider settings
- **`sensors.py`** - Hardware monitoring (CPU/GPU temperature) with multiple providers
- **`resilience.py`** - API resilience framework (TTL cache, circuit breaker pattern)
- **`triggers_external.py`** - External API integration with fallback support
- **`config.py`** - Legacy configuration management (being phased out)
- **`requirements_app.txt`** - Full application dependencies including hardware monitoring
- **`requirements_minimal.txt`** - Minimal runtime dependencies for basic functionality
- **`default_config.json`** - Default application settings with telemetry defaults
- **`cache/`** - Directory for API response caching and circuit breaker state
- **`tests/`** - Unit tests for resilience and core functionality
- **`assets/`** - Application assets (tray icons, etc.)

## ⚙️ Features

### 🎯 Real-time Monitoring
- **Keyboard Input Detection** - Tracks typing activity and calculates WPM
- **System Statistics** - Monitors CPU and RAM usage
- **Hardware Temperature Monitoring** - Optional CPU/GPU temperature display (Windows)
- **Time Display** - Sends current time to ESP32

### 🔗 Communication
- **Automatic ESP32 Detection** - Finds and connects to your Bongo Cat device
- **Serial Protocol** - Sends formatted commands over USB serial
- **Connection Management** - Handles reconnection and error recovery

### 🛡️ API Resilience
- **Circuit Breaker Pattern** - Prevents app crashes from external API failures
- **TTL Caching** - Caches API responses to reduce network load and improve reliability
- **Fallback Mechanisms** - Graceful degradation when external services unavailable
- **Telemetry & Monitoring** - Built-in metrics for debugging and optimization

### 🎛️ User Interface
- **System Tray Operation** - Runs quietly in background
- **Settings GUI** - Easy configuration with consent-based hardware monitoring
- **Visual Feedback** - Shows connection status, activity, and sensor data
- **Privacy Controls** - Opt-in consent required for hardware monitoring

## 🚀 Setup Instructions

### Prerequisites
```bash
pip install -r requirements_app.txt
```

**Core Dependencies**:
- `psutil` - System monitoring (CPU, RAM)
- `pyserial` - Serial communication with ESP32
- `requests` - HTTP client for external APIs
- `tkinter` - GUI framework (usually included with Python)

**Optional Dependencies** (for hardware monitoring):
- `keyboard` - Alternative keyboard monitoring (fallback for pynput)
- `nvidia-ml-py3` - NVIDIA GPU temperature monitoring (Windows only)

### Hardware Monitoring Setup (Optional - Windows Only)

1. **Install additional dependencies**:
   ```bash
   pip install nvidia-ml-py3  # For NVIDIA GPU monitoring
   ```

2. **Configure in application**:
   - Launch the app and open Settings → Advanced tab
   - Check "I consent to hardware temperature monitoring"
   - Check "Enable hardware temperature monitoring"
   - Select provider: "auto" (recommended), "lhm_http", or "nvml"
   - Test connectivity with "Test Sensors" button

**Privacy & Security**:
- Hardware monitoring requires explicit user consent
- GPU-only mode works without administrator privileges
- No data is transmitted externally - everything stays local
- Circuit breaker pattern prevents crashes from sensor failures

### Running from Source
```bash
cd bongo_cat_app
python main.py
```

### Building Executable
The project includes PyInstaller configuration for creating a standalone executable:
```bash
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## ⚙️ Configuration

Settings are stored in `settings.json` (managed by `settings.py`) and include:

### Display Settings
```json
{
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

### Telemetry & Hardware Monitoring
```json
{
  "telemetry": {
    "hardware_monitoring_enabled": false,
    "hardware_monitoring_consented": false,
    "provider": "auto",
    "gpu_only": true
  }
}
```

### Behavior Settings
```json
{
  "behavior": {
    "sleep_timeout": 300,
    "animation_speed": 1.0,
    "wpm_calculation_window": 10
  }
}
```

### Connection Settings
```json
{
  "connection": {
    "auto_connect": true,
    "baud_rate": 115200,
    "reconnect_delay": 5
  }
}
```

## 📡 Communication Protocol

The app sends commands to ESP32 via serial at 115200 baud:

| Command | Format | Description |
|---------|--------|-------------|
| CPU | `CPU:XX` | CPU usage percentage (0-100) |
| RAM | `RAM:XX` | RAM usage percentage (0-100) |
| WPM | `WPM:XX` | Words per minute (0-999) |
| TIME | `TIME:HH:MM` | Current time in 24h format |
| ANIM | `ANIM:X` | Animation state (0-9) |
| CPUTEMP | `CPUTEMP:XX.X` | CPU temperature in Celsius |
| GPUTEMP | `GPUTEMP:XX.X` | GPU temperature in Celsius |

## 🔧 Development

### Code Structure
- **Object-oriented design** with clear separation of concerns
- **Threading** for non-blocking operation
- **Error handling** for robust operation
- **Logging** for debugging and troubleshooting

### Key Classes
- `BongoCatEngine` - Main application logic
- `ConfigManager` - Settings management
- `SystemTray` - Tray icon and menu
- `SettingsGUI` - Configuration interface

### Adding Features
1. **Extend the engine** - Add new monitoring capabilities
2. **Update the protocol** - Define new command formats
3. **Modify the GUI** - Add configuration options
4. **Test thoroughly** - Ensure stability and performance

## 🐛 Troubleshooting

### Common Issues
- **ESP32 not detected**: Check USB drivers and COM port
- **High CPU usage**: Adjust monitoring intervals in config
- **Connection drops**: Verify cable connection and power

### Debug Mode
Run with debug logging:
```bash
python main.py --debug
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- **Cross-platform support** (macOS, Linux)
- **Additional system metrics** (network, disk usage)
- **Plugin system** for custom monitoring
- **UI improvements** and themes

---

*Keep your Bongo Cat happy with real-time data!* 🐱💻 