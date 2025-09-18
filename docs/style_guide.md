# CatJAM Monitor - Development Style Guide

## Overview

This style guide establishes coding standards, documentation practices, and development workflows for the CatJAM Monitor project. The project uses multiple technologies (Python, JavaScript, C++, Arduino) and this guide ensures consistency across all components.

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Development](#python-development)
3. [JavaScript/Node.js Development](#javascriptnodejs-development)
4. [Arduino/C++ Development](#arduinoc-development)
5. [Documentation Standards](#documentation-standards)
6. [Version Control](#version-control)
7. [Testing Standards](#testing-standards)
8. [Security Guidelines](#security-guidelines)

## General Principles

### Code Quality
- **Readability First**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns within each technology stack
- **Maintainability**: Write code that can be easily modified and extended
- **Performance**: Optimize for the target platform (desktop vs embedded)

### Naming Conventions
- **Descriptive Names**: Use clear, descriptive names for variables, functions, and classes
- **Consistent Casing**: Follow language-specific conventions
- **No Abbreviations**: Avoid unclear abbreviations unless they are well-established

### File Organization
- **Logical Grouping**: Group related files in appropriate directories
- **Clear Structure**: Use consistent directory structures across components
- **Separation of Concerns**: Keep different responsibilities in separate files

## Python Development

### Code Style (PEP 8)
```python
# Good: Clear, readable, follows PEP 8
def process_keyboard_input(key_event, trigger_manager):
    """Process a keyboard event and check for triggers."""
    if key_event.is_character:
        trigger_manager.check_triggers(key_event.char)
        return True
    return False

# Bad: Poor naming, no documentation, violates PEP 8
def proc_key(k, tm):
    if k.is_char:
        tm.chk_trig(k.c)
        return 1
    return 0
```

### Documentation Standards
- **Module Docstrings**: Every Python file should start with a module docstring
- **Function Docstrings**: All public functions need docstrings with parameters and return values
- **Type Hints**: Use type hints for function parameters and return values
- **Inline Comments**: Explain complex logic, not obvious operations

```python
"""
Imgflip API integration module.

This module handles fetching trending memes and managing API requests
for dynamic trigger generation.

Author: dentity007
Version: 2.0.0
"""

from typing import Optional, Dict, Any, List
import requests

class ImgflipIntegration:
    """Handles Imgflip API integration for dynamic triggers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Imgflip integration with optional configuration.

        Args:
            config: Optional dictionary containing API settings
        """
        self.config = config or {}
        self.base_url = "https://api.imgflip.com"
        self.timeout = self.config.get('timeout', 10)

    def fetch_trending_memes(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Fetch trending memes from Imgflip API.

        Args:
            limit: Maximum number of memes to fetch

        Returns:
            List of meme dictionaries, or None if request fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/get_memes",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            memes = data.get('data', {}).get('memes', [])

            # Return top memes by popularity/usage
            return memes[:limit]

        except requests.RequestException as e:
            print(f"Imgflip API request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def generate_triggers(self, memes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate trigger configurations from meme data.

        Args:
            memes: List of meme dictionaries from API

        Returns:
            List of trigger configurations
        """
        triggers = []

        for meme in memes:
            # Create trigger based on meme name
            trigger_word = self._normalize_trigger(meme['name'])

            trigger = {
                'trigger': trigger_word,
                'response': f"Viral: {meme['name']}—cat's got the meme! 😂",
                'animation': 'meme_surprise',
                'source': 'imgflip',
                'meme_id': meme['id']
            }

            triggers.append(trigger)

        return triggers
```

### Error Handling
- **Specific Exceptions**: Catch specific exceptions rather than generic `Exception`
- **Meaningful Messages**: Provide clear error messages for debugging
- **Graceful Degradation**: Handle errors gracefully without crashing the application
- **Logging**: Use appropriate logging levels (DEBUG, INFO, WARNING, ERROR)

```python
import logging

logger = logging.getLogger(__name__)

def safe_api_request(url, timeout=10, max_retries=3):
    """Safely make API requests with proper error handling and retries."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            logger.info(f"API request successful: {url}")
            return response.json()

        except requests.Timeout:
            logger.warning(f"API request timeout (attempt {attempt + 1}/{max_retries}): {url}")
        except requests.HTTPError as e:
            logger.error(f"API HTTP error: {e.response.status_code} - {url}")
            break  # Don't retry HTTP errors
        except requests.RequestException as e:
            logger.error(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    logger.error(f"All API request attempts failed: {url}")
    return None
        posts = list(subreddit.hot(limit=10))
        logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit_name}")
        return posts
    except praw.exceptions.APIException as e:
        logger.error(f"Reddit API error for r/{subreddit_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching r/{subreddit_name}: {e}")
        return []
```

### Testing Standards
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Mock External Dependencies**: Use mocks for API calls and hardware interactions
- **Test Coverage**: Aim for 80%+ code coverage

```python
# tests/test_reddit_authenticator.py
import pytest
from unittest.mock import Mock, patch
from src.reddit_authenticator import RedditAuthenticator

class TestRedditAuthenticator:
    def test_successful_authentication(self, mock_config):
        """Test successful Reddit authentication."""
        with patch('praw.Reddit') as mock_reddit_class:
            mock_reddit_instance = Mock()
            mock_user = Mock()
            mock_user.name = 'testuser'
            mock_reddit_instance.user.me.return_value = mock_user
            mock_reddit_class.return_value = mock_reddit_instance

            auth = RedditAuthenticator(mock_config)
            result = auth.authenticate()

            assert result is not None
            mock_reddit_class.assert_called_once()

    def test_missing_config_raises_error(self):
        """Test that missing configuration raises ValueError."""
        incomplete_config = {'client_id': 'test'}

        with pytest.raises(ValueError) as exc_info:
            RedditAuthenticator(incomplete_config)

        assert 'Missing required configuration keys' in str(exc_info.value)
```

## JavaScript/Node.js Development

### Code Style (Airbnb Style Guide)
```javascript
// Good: Clear, consistent, well-documented
/**
 * Process keyboard input and check for triggers
 * @param {KeyboardEvent} keyEvent - The keyboard event object
 * @param {TriggerManager} triggerManager - Manager for handling triggers
 * @returns {boolean} True if trigger was processed
 */
function processKeyboardInput(keyEvent, triggerManager) {
  if (keyEvent.isCharacter) {
    triggerManager.checkTriggers(keyEvent.char);
    return true;
  }
  return false;
}

// Bad: Poor naming, inconsistent style, no documentation
function procKey(k, tm) {
  if (k.isChar) {
    tm.chkTrig(k.c);
    return 1;
  }
  return 0;
}
```

### Documentation Standards
- **JSDoc Comments**: Use JSDoc for all public functions and classes
- **Type Annotations**: Use JSDoc type annotations for parameters and return values
- **Module Documentation**: Document module purpose and exports
- **Inline Comments**: Explain complex logic and business rules

```javascript
/**
 * ESP32 Serial Communication Manager
 *
 * Handles connection, data transmission, and protocol implementation
 * for communicating with ESP32 hardware via serial port.
 *
 * @class ESP32SerialManager
 */
class ESP32SerialManager {
  /**
   * Initialize the serial manager
   * @param {EventEmitter} eventEmitter - Application event emitter
   */
  constructor(eventEmitter) {
    this.eventEmitter = eventEmitter;
    this.port = null;
    this.isConnected = false;

    // Command queue for reliable transmission
    this.commandQueue = [];
    this.isProcessingQueue = false;
  }

  /**
   * Connect to ESP32 via serial port
   * @param {string} portPath - Serial port path (e.g., '/dev/ttyUSB0')
   * @returns {Promise<boolean>} True if connection successful
   */
  async connect(portPath) {
    try {
      this.port = new SerialPort({
        path: portPath,
        baudRate: 115200,
        dataBits: 8,
        parity: 'none',
        stopBits: 1
      });

      return new Promise((resolve) => {
        this.port.on('open', () => {
          this.isConnected = true;
          console.log(`Connected to ESP32 on ${portPath}`);
          resolve(true);
        });

        this.port.on('error', (error) => {
          console.error('Serial port error:', error);
          resolve(false);
        });
      });
    } catch (error) {
      console.error('Failed to connect to serial port:', error);
      return false;
    }
  }

  /**
   * Send command to ESP32 with error handling
   * @param {string} command - Command to send
   * @returns {Promise<boolean>} True if command sent successfully
   */
  async sendCommand(command) {
    if (!this.isConnected || !this.port) {
      console.error('Not connected to ESP32');
      return false;
    }

    return new Promise((resolve) => {
      this.port.write(`${command}\n`, (error) => {
        if (error) {
          console.error('Error sending command:', error);
          resolve(false);
        } else {
          console.log(`Sent command: ${command}`);
          resolve(true);
        }
      });
    });
  }
}

module.exports = ESP32SerialManager;
```

### Asynchronous Code
- **Async/Await**: Prefer async/await over Promises for readability
- **Error Handling**: Always handle promise rejections
- **Timeouts**: Implement timeouts for long-running operations
- **Cancellation**: Support operation cancellation where appropriate

```javascript
/**
 * Fetch data from API with timeout and error handling
 * @param {string} url - API endpoint URL
 * @param {number} timeoutMs - Timeout in milliseconds
 * @returns {Promise<Object>} API response data
 */
async function fetchWithTimeout(url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timed out');
    }

    throw error;
  }
}
```

## Arduino/C++ Development

### Code Style (Google C++ Style Guide)
```cpp
// Good: Clear structure, proper naming, well-documented
/**
 * Process incoming serial commands from Python application
 * @param command The command string to process
 */
void processCommand(String command) {
  Serial.println("Received command: " + command);

  if (command.startsWith("MEME:")) {
    // Extract meme text and animation from command
    String memeData = command.substring(5);
    int separatorIndex = memeData.indexOf('|');

    if (separatorIndex > 0) {
      String text = memeData.substring(0, separatorIndex);
      String animation = memeData.substring(separatorIndex + 1);
      displayMeme(text, animation);
    } else {
      displayMeme(memeData, "default");
    }
  } else if (command.startsWith("CPU:")) {
    int cpuValue = command.substring(4).toInt();
    updateCPU(cpuValue);
  }
  // ... additional command handling
}

// Bad: Poor structure, unclear naming, no documentation
void procCmd(String c) {
  Serial.println(c);
  if (c.startsWith("MEME:")) {
    String d = c.substring(5);
    int i = d.indexOf('|');
    if (i > 0) {
      String t = d.substring(0, i);
      String a = d.substring(i + 1);
      dispMeme(t, a);
    }
  }
}
```

### Documentation Standards
- **Function Comments**: Document all public functions with purpose and parameters
- **Class Comments**: Document class purpose and responsibilities
- **Inline Comments**: Explain hardware interactions and complex logic
- **Pin Definitions**: Document hardware pin usage and connections

```cpp
/**
 * CatJAM Monitor ESP32 Firmware
 *
 * Arduino firmware for ESP32-based Bongo Cat display monitor.
 * Receives commands from Python application via serial communication
 * and displays memes, animations, and system information on TFT LCD.
 *
 * Hardware Requirements:
 * - ESP32 Dev Board (ESP32-WROOM-32)
 * - 2.8" ILI9341 TFT LCD Display (320x240)
 * - Proper wiring connections (see pin definitions below)
 *
 * Communication Protocol:
 * - Baud Rate: 115200
 * - Commands: MEME:text|animation, CPU:value, RAM:value, etc.
 *
 * Author: dentity007
 * Version: 1.0.0
 * Date: September 2025
 */

// =============================================================================
// PIN DEFINITIONS AND HARDWARE CONFIGURATION
// =============================================================================

// TFT LCD Pin Configuration
#define TFT_CS   5    // Chip Select - Controls TFT communication
#define TFT_DC   4    // Data/Command - TFT data/command mode selection
#define TFT_RST  22   // Reset - TFT reset signal
#define TFT_SCK  18   // SPI Clock - SPI communication clock
#define TFT_MOSI 23   // SPI Data Out - SPI data transmission
#define TFT_MISO 19   // SPI Data In - SPI data reception (optional)

// LED Pin for status indication
#define LED_PIN  2    // Built-in LED for visual status feedback

// SPI Bus Configuration
#define SPI_FREQUENCY  27000000  // 27MHz SPI frequency for TFT
#define SPI_MODE       SPI_MODE0 // SPI mode for TFT communication

// =============================================================================
// LIBRARY INCLUDES AND DEPENDENCIES
// =============================================================================

// TFT and Graphics Libraries
#include <TFT_eSPI.h>        // TFT LCD driver library
#include <SPI.h>            // SPI communication library
#include <lvgl.h>           // Light and Versatile Graphics Library

// Standard Libraries
#include <Wire.h>           // I2C communication (if needed)
#include <WiFi.h>           // WiFi support (future feature)

// =============================================================================
// GLOBAL OBJECTS AND STATE VARIABLES
// =============================================================================

// TFT Display Object
TFT_eSPI tft = TFT_eSPI();

// LVGL Display Buffer (for advanced graphics)
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[TFT_WIDTH * 10];

// Display and Animation State
String currentAnimation = "idle";      // Current animation state
String currentText = "";               // Currently displayed text
bool displayActive = true;             // Display power state
unsigned long lastUpdateTime = 0;      // Last display update timestamp
const unsigned long UPDATE_INTERVAL = 100; // Display update frequency (ms)

// Communication State
bool serialConnected = false;          // Serial connection status
unsigned long lastCommandTime = 0;     // Last received command timestamp
const unsigned long COMMAND_TIMEOUT = 5000; // Command timeout (ms)

// =============================================================================
// ARDUINO SETUP FUNCTION
// =============================================================================

/**
 * Arduino setup function - initializes hardware and software components
 *
 * This function is called once when the ESP32 boots up. It initializes:
 * - Serial communication for debugging and command reception
 * - TFT display hardware and graphics libraries
 * - GPIO pins for LED and other peripherals
 * - LVGL graphics system for advanced UI
 * - WiFi (if enabled for future features)
 */
void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  Serial.println("CatJAM Firmware Ready!");

  // Initialize TFT Display
  tft.init();
  tft.setRotation(1);  // Landscape orientation for better viewing
  tft.fillScreen(TFT_BLACK);  // Clear screen to black

  // Initialize LVGL Graphics System
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, buf, NULL, TFT_WIDTH * 10);

  // Create LVGL display driver for advanced graphics
  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = TFT_WIDTH;
  disp_drv.ver_res = TFT_HEIGHT;
  disp_drv.flush_cb = my_disp_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  // Initialize GPIO pins
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // Turn on LED to indicate ready state

  // Display startup message on TFT
  tft.setCursor(10, 10);
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(2);
  tft.println("CatJAM Ready!");
  tft.println("Waiting for commands...");

  Serial.println("ESP32 TFT Display initialized successfully");
  serialConnected = true;
}

// =============================================================================
// ARDUINO MAIN LOOP
// =============================================================================

/**
 * Arduino main loop - handles continuous operation
 *
 * This function runs continuously after setup() completes. It:
 * - Processes incoming serial commands from the Python application
 * - Updates the display with animations and status information
 * - Handles LVGL graphics rendering
 * - Manages system state and error conditions
 */
void loop() {
  // Process incoming serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace and newlines

    // Process the command and update timestamp
    processCommand(command);
    lastCommandTime = millis();
  }

  // Update LVGL graphics system (for animations and UI)
  lv_timer_handler();
  lv_tick_inc(UPDATE_INTERVAL);

  // Periodic display updates (animations, status, etc.)
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
    updateDisplay();
    lastUpdateTime = currentTime;
  }

  // Check for command timeout (indicates Python app might be disconnected)
  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    handleCommandTimeout();
  }

  // Small delay to prevent overwhelming the processor
  delay(10);
}

// =============================================================================
// COMMAND PROCESSING FUNCTIONS
// =============================================================================

/**
 * Process incoming serial commands from Python application
 *
 * Supported Commands:
 * - MEME:text|animation - Display meme with specific animation
 * - CPU:value - Update CPU usage display
 * - RAM:value - Update RAM usage display
 * - WPM:value - Update typing speed display
 * - TIME:hh:mm - Update time display
 * - ANIM:id - Change animation
 * - STATUS:text - Display status message
 * - PING - Connection test command
 *
 * @param command The command string to process
 */
void processCommand(String command) {
  Serial.println("Received command: " + command);

  if (command.startsWith("MEME:")) {
    // Extract meme text and animation from command
    String memeData = command.substring(5);  // Remove "MEME:" prefix
    int separatorIndex = memeData.indexOf('|');

    if (separatorIndex > 0) {
      String text = memeData.substring(0, separatorIndex);
      String animation = memeData.substring(separatorIndex + 1);
      displayMeme(text, animation);
    } else {
      displayMeme(memeData, "default");
    }

  } else if (command.startsWith("CPU:")) {
    int cpuValue = command.substring(4).toInt();
    updateCPU(cpuValue);

  } else if (command.startsWith("RAM:")) {
    int ramValue = command.substring(4).toInt();
    updateRAM(ramValue);

  } else if (command.startsWith("WPM:")) {
    int wpmValue = command.substring(4).toInt();
    updateWPM(wpmValue);

  } else if (command.startsWith("TIME:")) {
    String timeString = command.substring(5);
    updateTime(timeString);

  } else if (command.startsWith("ANIM:")) {
    String animationId = command.substring(5);
    changeAnimation(animationId);

  } else if (command.startsWith("STATUS:")) {
    String statusText = command.substring(7);
    displayStatus(statusText);

  } else if (command == "PING") {
    // Respond to ping for connection testing
    Serial.println("PONG");
    blinkLED(1, 100);  // Brief LED blink to indicate ping received

  } else {
    Serial.println("Unknown command: " + command);
    // Could send error response back to Python app
  }
}

// =============================================================================
// DISPLAY FUNCTIONS
// =============================================================================

/**
 * Display a meme with specified text and animation
 * @param text The meme text to display
 * @param animation The animation type to play
 */
void displayMeme(String text, String animation) {
  Serial.println("Displaying meme: " + text + " with animation: " + animation);

  // Clear display for new content
  tft.fillScreen(TFT_BLACK);

  // Set text properties for meme display
  tft.setCursor(10, 50);
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(2);

  // Display the meme text
  tft.println(text);

  // TODO: Implement animation system
  // playAnimation(animation);

  // Update current state
  currentText = text;
  currentAnimation = animation;

  // Visual feedback - blink LED when meme is displayed
  blinkLED(2, 200);
}

/**
 * Update CPU usage display in corner of screen
 * @param cpuPercent CPU usage percentage (0-100)
 */
void updateCPU(int cpuPercent) {
  // Clear previous CPU value area
  tft.fillRect(250, 200, 60, 30, TFT_BLACK);

  // Display new CPU value
  tft.setCursor(250, 200);
  tft.setTextColor(TFT_RED);
  tft.setTextSize(1);
  tft.printf("CPU:%d%%", cpuPercent);
}

/**
 * Update RAM usage display in corner of screen
 * @param ramPercent RAM usage percentage (0-100)
 */
void updateRAM(int ramPercent) {
  // Clear previous RAM value area
  tft.fillRect(250, 180, 60, 30, TFT_BLACK);

  // Display new RAM value
  tft.setCursor(250, 180);
  tft.setTextColor(TFT_BLUE);
  tft.setTextSize(1);
  tft.printf("RAM:%d%%", ramPercent);
}

/**
 * Update typing speed display
 * @param wpm Words per minute value
 */
void updateWPM(int wpm) {
  // Clear previous WPM value area
  tft.fillRect(10, 200, 60, 30, TFT_BLACK);

  // Display new WPM value
  tft.setCursor(10, 200);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(1);
  tft.printf("WPM:%d", wpm);
}

/**
 * Update time display in top center
 * @param timeString Time string in format "HH:MM"
 */
void updateTime(String timeString) {
  // Clear previous time area
  tft.fillRect(120, 10, 80, 20, TFT_BLACK);

  // Display new time
  tft.setCursor(120, 10);
  tft.setTextColor(TFT_YELLOW);
  tft.setTextSize(1);
  tft.println(timeString);
}

/**
 * Change current animation
 * @param animationId The ID of the animation to switch to
 */
void changeAnimation(String animationId) {
  Serial.println("Changing animation to: " + animationId);
  currentAnimation = animationId;

  // TODO: Implement animation switching logic
  // loadAnimation(animationId);
  // startAnimation();
}

/**
 * Display status message at bottom of screen
 * @param statusText The status message to display
 */
void displayStatus(String statusText) {
  // Clear previous status area
  tft.fillRect(10, 220, 300, 20, TFT_BLACK);

  // Display new status
  tft.setCursor(10, 220);
  tft.setTextColor(TFT_CYAN);
  tft.setTextSize(1);
  tft.println(statusText);
}

// =============================================================================
// LVGL DISPLAY FLUSH CALLBACK
// =============================================================================

/**
 * LVGL display flush callback function
 * Transfers LVGL buffer to TFT display via SPI
 *
 * This function is called by LVGL when the display needs to be updated.
 * It handles the low-level SPI communication with the TFT display.
 *
 * @param disp Pointer to LVGL display driver
 * @param area Pointer to area that needs to be updated
 * @param color_p Pointer to color data buffer
 */
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  uint32_t width = (area->x2 - area->x1 + 1);
  uint32_t height = (area->y2 - area->x1 + 1);

  // Start SPI transaction for TFT update
  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, width, height);

  // Transfer color data to TFT
  tft.pushColors(&color_p->full, width * height, true);
  tft.endWrite();

  // Notify LVGL that flush is complete
  lv_disp_flush_ready(disp);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Periodic display updates (animations, status, etc.)
 * Called regularly from main loop to update display state
 */
void updateDisplay() {
  // TODO: Implement animation frames
  // TODO: Update status indicators
  // TODO: Handle display timeouts
  // TODO: Update system monitoring displays

  // Example: Update connection status indicator
  if (serialConnected) {
    tft.fillCircle(310, 10, 5, TFT_GREEN);  // Green dot for connected
  } else {
    tft.fillCircle(310, 10, 5, TFT_RED);    // Red dot for disconnected
  }
}

/**
 * Handle command timeout (Python app might be disconnected)
 * Called when no commands received for an extended period
 */
void handleCommandTimeout() {
  // Visual indication of timeout
  tft.fillRect(10, 220, 300, 20, TFT_BLACK);
  tft.setCursor(10, 220);
  tft.setTextColor(TFT_RED);
  tft.setTextSize(1);
  tft.println("Connection timeout - waiting for commands...");

  // Blink LED to indicate timeout
  blinkLED(3, 500);

  // Reset connection status
  serialConnected = false;
}

/**
 * Blink LED for status indication
 * @param times Number of times to blink
 * @param delayMs Delay between blinks in milliseconds
 */
void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}

// =============================================================================
// TODO LIST AND FUTURE FEATURES
// =============================================================================

/*
TODO: Implement these features:

1. Animation System:
   - Load animation frames from PROGMEM
   - Implement frame timing and transitions
   - Add different animation states (idle, typing, meme)

2. Graphics Enhancements:
   - Add Bongo Cat sprite animations
   - Implement text bubbles for memes
   - Add background images and themes

3. Communication Improvements:
   - Add command acknowledgment system
   - Implement error handling for malformed commands
   - Add command queue for reliable transmission

4. Hardware Features:
   - Add touch screen support
   - Implement sound output
   - Add WiFi connectivity for remote control

5. Power Management:
   - Implement sleep modes
   - Add automatic display timeout
   - Optimize for battery operation

6. System Monitoring:
   - Add temperature monitoring
   - Implement network status display
   - Add battery level monitoring (if applicable)
*/
```

### Memory Management
- **PROGMEM**: Store large data (images, fonts) in flash memory
- **Stack vs Heap**: Be mindful of limited RAM (520KB on ESP32)
- **Buffer Sizes**: Use appropriate buffer sizes to prevent overflow
- **Memory Pools**: Consider using memory pools for frequent allocations

```cpp
// Store animation frames in flash memory to save RAM
const uint16_t animation_frames[] PROGMEM = {
  0x0000, 0xFFFF, 0xFFFF, 0x0000,  // Frame 1
  0xFFFF, 0x0000, 0x0000, 0xFFFF,  // Frame 2
  // ... more frames
};

// Safe string buffer handling
#define MAX_COMMAND_LENGTH 256
char commandBuffer[MAX_COMMAND_LENGTH];

void processSerialData() {
  static uint8_t bufferIndex = 0;

  while (Serial.available() && bufferIndex < MAX_COMMAND_LENGTH - 1) {
    char incomingByte = Serial.read();
    commandBuffer[bufferIndex++] = incomingByte;

    if (incomingByte == '\n') {
      commandBuffer[bufferIndex - 1] = '\0';  // Null terminate
      processCommand(String(commandBuffer));
      bufferIndex = 0;  // Reset buffer
    }
  }

  // Handle buffer overflow
  if (bufferIndex >= MAX_COMMAND_LENGTH - 1) {
    Serial.println("ERROR: Command too long");
    bufferIndex = 0;
  }
}
```

## Documentation Standards

### README Files
- **Clear Structure**: Use consistent headings and sections
- **Installation Instructions**: Step-by-step setup guide
- **Usage Examples**: Practical code examples
- **Troubleshooting**: Common issues and solutions
- **Contributing Guide**: How others can contribute

### API Documentation
- **Function Signatures**: Complete parameter and return value documentation
- **Usage Examples**: Code examples for common use cases
- **Error Handling**: Document exceptions and error conditions
- **Version Information**: API version and compatibility notes

### Inline Documentation
- **Purpose**: Explain why code exists, not just what it does
- **Context**: Provide context for complex business logic
- **Assumptions**: Document assumptions and limitations
- **References**: Link to external documentation or specifications

## Version Control

### Git Workflow
- **Feature Branches**: Create branches for new features
- **Descriptive Commits**: Write clear, descriptive commit messages
- **Pull Requests**: Use PRs for code review and integration
- **Branch Naming**: Use consistent naming conventions

```bash
# Good commit messages
git commit -m "feat: add Reddit API integration for dynamic triggers

- Implement PRAW authentication
- Add trigger fetching from r/memes
- Handle API rate limits gracefully
- Add fallback to static triggers on failure"

# Bad commit message
git commit -m "fixed stuff"
```

### Branch Naming Convention
```
feature/add-reddit-integration     # New features
bugfix/serial-connection-issue     # Bug fixes
hotfix/critical-security-patch     # Critical fixes
refactor/cleanup-old-code          # Code refactoring
docs/update-api-documentation      # Documentation updates
```

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Testing Standards

### Test Organization
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test speed and resource usage

### Test Naming Convention
```python
# Unit tests
def test_calculate_trigger_score():
def test_validate_reddit_credentials():
def test_process_keyboard_event():

# Integration tests
def test_full_trigger_workflow():
def test_esp32_communication_cycle():
def test_reddit_api_integration():
```

### Test Coverage Goals
- **Critical Paths**: 100% coverage for core functionality
- **Error Handling**: Test all error conditions
- **Edge Cases**: Test boundary conditions and unusual inputs
- **Performance**: Test under load and stress conditions

### Mocking Strategy
- **External APIs**: Mock Reddit API, serial ports, file systems
- **Hardware**: Mock ESP32 communication, display operations
- **Time-dependent**: Mock timers, delays, and scheduling

## Security Guidelines

### Input Validation
- **Sanitize Inputs**: Validate and sanitize all user inputs
- **Type Checking**: Verify data types and ranges
- **SQL Injection**: Use parameterized queries (if applicable)
- **XSS Prevention**: Escape HTML content in web interfaces

### Authentication
- **Secure Storage**: Never store credentials in plain text
- **Environment Variables**: Use .env files for sensitive data
- **Token Management**: Implement proper token expiration and refresh
- **Rate Limiting**: Protect against brute force attacks

### Network Security
- **HTTPS Only**: Use secure connections for web interfaces
- **CORS Policy**: Implement proper CORS headers
- **Input Validation**: Validate all network inputs
- **Error Handling**: Don't expose internal errors to users

### Code Security
- **Dependency Updates**: Keep dependencies updated and secure
- **Code Reviews**: Review all code changes for security issues
- **Secrets Management**: Never commit secrets to version control
- **Access Control**: Implement proper access controls

---

## Implementation Checklist

Use this checklist when implementing new features:

### Pre-Implementation
- [ ] Design reviewed and approved
- [ ] Requirements documented
- [ ] Test cases written
- [ ] Security review completed

### During Implementation
- [ ] Code follows style guide
- [ ] Functions properly documented
- [ ] Error handling implemented
- [ ] Security considerations addressed
- [ ] Tests passing

### Post-Implementation
- [ ] Code reviewed by peer
- [ ] Documentation updated
- [ ] Tests added to CI/CD
- [ ] Performance tested
- [ ] Security tested

---

*Style Guide Version: 1.0.0 | Last Updated: September 2025*