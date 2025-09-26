/*
 * Bongo Cat Monitor Firmware
 *
 * ESP32 firmware for the Bongo Cat Monitor - a remix with enhanced features
 *
 * Original project by Vostok Labs:
 * https://github.com/vostoklabs/bongo_cat_monitor
 *
 * This remix adds meme triggers, improved animations, and enhanced functionality
 * while building on the solid foundation provided by the original project.
 *
 * Author: dentity007 (remix)
 * Original: Vostok Labs
 * License: MIT
 */

#include <lvgl.h>
#include <TFT_eSPI.h>
#include <WiFi.h>
#include <EEPROM.h>
#include "Free_Fonts.h"
#include "animations_sprites.h"

// Include modular headers
#include "config.h"
#include "display.h"
#include "animation.h"
#include "serial.h"
#include "stats.h"

// Global TFT instance
TFT_eSPI tft = TFT_eSPI();

// Forward declarations
const char* get_state_name(animation_state_t state);

// Display settings
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 320

// Enhanced animation control
bool python_control_mode = true;  // Python controls idle progression
uint32_t last_command_time = 0;   // Track when last command received
#define TYPING_TIMEOUT_MS 2000    // Stop typing animation after 2 seconds of no commands
#define PYTHON_TIMEOUT_MS 5000    // Fall back to auto mode after 5 seconds

// Simplified animation performance (removed aggressive frame limiting)
uint32_t frame_skip_counter = 0;

// Function to flush the display buffer
void my_disp_flush(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_map) {
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors((uint16_t*)color_map, w * h, true);
    tft.endWrite();

    lv_disp_flush_ready(drv);
}

// Sprite management functions are now in animation.cpp
// Serial command handling is now in serial.cpp
// Display functions are now in display.cpp
// Configuration functions are now in config.cpp
// Stats functions are now in stats.cpp

void setup() {
    Serial.begin(115200);
    Serial.println("🐱 Bongo Cat with Sprites Starting...");

    // Initialize EEPROM for settings persistence
    EEPROM.begin(EEPROM_SIZE);

    // Load settings from EEPROM (will use defaults if invalid)
    loadSettings();

    // Initialize random seed for animations
    randomSeed(analogRead(0));

    tft.init();
    tft.setRotation(0);
    tft.fillScreen(TFT_WHITE);  // White background

    // Initialize LVGL with simpler setup
    lv_init();

    // Create display driver for LVGL v8
    static lv_disp_draw_buf_t draw_buf;
    static lv_color_t buf2[SCREEN_WIDTH * 10];
    lv_disp_draw_buf_init(&draw_buf, buf, buf2, SCREEN_WIDTH * 10);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = SCREEN_WIDTH;
    disp_drv.ver_res = SCREEN_HEIGHT;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    // Initialize sprite manager
    sprite_manager_init(&sprite_manager);

    // Create the Bongo Cat UI
    createBongoCat();

    // Apply loaded settings to display visibility now that UI is created
    updateDisplayVisibility();

    Serial.println("✅ Bongo Cat Ready!");
}

void loop() {
    handleSerialCommands();

    uint32_t current_time = millis();

    // Update animations - removed fixed frame rate to prevent conflicts
    static uint32_t last_animation_update = 0;
    if (current_time - last_animation_update >= 25) {  // 40 FPS max (more responsive)
        sprite_manager_update(&sprite_manager, current_time);

        // Only render if sprites actually changed to reduce canvas operations
        static uint32_t last_sprite_hash = 0;
        uint32_t current_sprite_hash = 0;

        // Calculate simple hash of current sprites to detect changes (optimized)
        for (int i = 0; i < NUM_LAYERS; i++) {
            current_sprite_hash += (uint32_t)sprite_manager.current_sprites[i];
        }

        // Only re-render if sprites changed or it's been too long (forced refresh)
        if (current_sprite_hash != last_sprite_hash || (current_time - last_animation_update) > 200) {
            sprite_render_layers(&sprite_manager, cat_canvas, current_time);
            last_sprite_hash = current_sprite_hash;
        }

        last_animation_update = current_time;
    }

    // Update time display every second
    static uint32_t last_time_update = 0;
    if (current_time - last_time_update >= 1000) {
        updateTimeDisplay();
        last_time_update = current_time;
    }

    // Clear meme text after 5 seconds
    if (meme_display_time > 0 && current_time - meme_display_time >= 5000) {
        tft.fillRect(0, 200, 240, 40, TFT_BLACK);  // Clear bottom area
        meme_display_time = 0;  // Reset timer
    }

    // Reduce LVGL timer handler frequency to prevent system overload
    static uint32_t last_lvgl_update = 0;
    if (current_time - last_lvgl_update >= 20) {  // 50 FPS max for LVGL (was every 5ms)
        lv_timer_handler();
        last_lvgl_update = current_time;
    }

    delay(2);  // Reduced from 5ms for better responsiveness
} 