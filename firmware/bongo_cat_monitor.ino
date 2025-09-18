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
// PIN DEFINITIONS
// =============================================================================

// TFT LCD Pin Configuration
#define TFT_CS   5    // Chip Select
#define TFT_DC   4    // Data/Command
#define TFT_RST  22   // Reset
#define TFT_SCK  18   // SPI Clock
#define TFT_MOSI 23   // SPI Data Out
#define TFT_MISO 19   // SPI Data In (optional)

// LED Pin (if available)
#define LED_PIN  2    // Built-in LED for status indication

// =============================================================================
// LIBRARY INCLUDES
// =============================================================================

// TFT and Graphics Libraries
#include <TFT_eSPI.h>        // TFT LCD driver
#include <SPI.h>            // SPI communication
#include <lvgl.h>           // Light and Versatile Graphics Library

// Standard Libraries
#include <Wire.h>           // I2C communication (if needed)
#include <WiFi.h>           // WiFi support (future feature)

// =============================================================================
// GLOBAL OBJECTS AND VARIABLES
// =============================================================================

// TFT Display Object
TFT_eSPI tft = TFT_eSPI();

// LVGL Display Buffer
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[ TFT_WIDTH * 10 ];

// Animation and Display State
String currentAnimation = "idle";
String currentText = "";
bool displayActive = true;
unsigned long lastUpdateTime = 0;
const unsigned long UPDATE_INTERVAL = 100; // 100ms update rate

// =============================================================================
// ARDUINO SETUP FUNCTION
// =============================================================================

void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  Serial.println("CatJAM Firmware Ready!");  // For testing

  // Initialize TFT Display
  tft.init();
  tft.setRotation(1);  // Landscape orientation
  tft.fillScreen(TFT_BLACK);  // Clear screen to black

  // Initialize LVGL
  lv_init();
  lv_disp_draw_buf_init(&draw_buf, buf, NULL, TFT_WIDTH * 10);

  // Create LVGL display driver
  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = TFT_WIDTH;
  disp_drv.ver_res = TFT_HEIGHT;
  disp_drv.flush_cb = my_disp_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  // Initialize LED for status indication
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // Turn on LED to indicate ready state

  // Display startup message
  tft.setCursor(10, 10);
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(2);
  tft.println("CatJAM Ready!");
  tft.println("Waiting for commands...");

  Serial.println("ESP32 TFT Display initialized successfully");
}

// =============================================================================
// ARDUINO MAIN LOOP
// =============================================================================

void loop() {
  // Check for incoming serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace

    // Process the command
    processCommand(command);
  }

  // Update LVGL (if using LVGL graphics)
  lv_timer_handler();
  lv_tick_inc(UPDATE_INTERVAL);

  // Handle periodic updates (animations, status displays)
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
    updateDisplay();
    lastUpdateTime = currentTime;
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

  } else {
    Serial.println("Unknown command: " + command);
  }
}

// =============================================================================
// DISPLAY FUNCTIONS
// =============================================================================

/**
 * Display a meme with specified text and animation
 */
void displayMeme(String text, String animation) {
  Serial.println("Displaying meme: " + text + " with animation: " + animation);

  // Clear display
  tft.fillScreen(TFT_BLACK);

  // Set text properties
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
}

/**
 * Update CPU usage display
 */
void updateCPU(int cpuPercent) {
  // Display CPU usage in corner
  tft.fillRect(250, 200, 60, 30, TFT_BLACK);  // Clear previous value
  tft.setCursor(250, 200);
  tft.setTextColor(TFT_RED);
  tft.setTextSize(1);
  tft.printf("CPU:%d%%", cpuPercent);
}

/**
 * Update RAM usage display
 */
void updateRAM(int ramPercent) {
  // Display RAM usage in corner
  tft.fillRect(250, 180, 60, 30, TFT_BLACK);  // Clear previous value
  tft.setCursor(250, 180);
  tft.setTextColor(TFT_BLUE);
  tft.setTextSize(1);
  tft.printf("RAM:%d%%", ramPercent);
}

/**
 * Update typing speed display
 */
void updateWPM(int wpm) {
  // Display WPM in corner
  tft.fillRect(10, 200, 60, 30, TFT_BLACK);  // Clear previous value
  tft.setCursor(10, 200);
  tft.setTextColor(TFT_GREEN);
  tft.setTextSize(1);
  tft.printf("WPM:%d", wpm);
}

/**
 * Update time display
 */
void updateTime(String timeString) {
  // Display time in top center
  tft.fillRect(120, 10, 80, 20, TFT_BLACK);  // Clear previous time
  tft.setCursor(120, 10);
  tft.setTextColor(TFT_YELLOW);
  tft.setTextSize(1);
  tft.println(timeString);
}

/**
 * Change current animation
 */
void changeAnimation(String animationId) {
  Serial.println("Changing animation to: " + animationId);
  currentAnimation = animationId;
  // TODO: Implement animation switching logic
}

/**
 * Display status message
 */
void displayStatus(String statusText) {
  // Display status in bottom area
  tft.fillRect(10, 220, 300, 20, TFT_BLACK);  // Clear previous status
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
 * Transfers LVGL buffer to TFT display
 */
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  uint32_t w = (area->x2 - area->x1 + 1);
  uint32_t h = (area->y2 - area->x1 + 1);

  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, w, h);
  tft.pushColors(&color_p->full, w * h, true);
  tft.endWrite();

  lv_disp_flush_ready(disp);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Periodic display updates (animations, status, etc.)
 */
void updateDisplay() {
  // TODO: Implement animation frames
  // TODO: Update status indicators
  // TODO: Handle display timeouts
}

/**
 * Blink LED for status indication
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
*/

import praw
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_ID'),
    client_secret=os.getenv('REDDIT_SECRET'),
    user_agent='CatJAM Monitor v1.0'
)

# Step 1: Test user auth
me = reddit.user.me()
print(f"✅ User auth: Logged in as {me.name}")

# Step 2: Test subreddit access (use 'test' first—super public, low rate limit)
subreddit = reddit.subreddit('test')
print("✅ Subreddit access: Can reach r/test")

# Step 3: Fetch hot posts
for post in subreddit.hot(limit=3):
    print(f"Hot post: {post.title} (score: {post.score})")

print("🎉 Full success—copy this logic to main.py!")