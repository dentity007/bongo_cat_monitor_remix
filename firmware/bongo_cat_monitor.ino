void setup() {
  Serial.begin(115200);
  Serial.println("CatJAM Firmware Ready!");  // For testing
  // TODO: Add LVGL/TFT setup from original Vostok project
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("MEME:")) {
      Serial.println("MEME fired: " + cmd);  // Echo for testing—replace with animation/bubble
      // TODO: playAnimation(cmd.substring(5)); showBubble(...);
    }
    // TODO: Add TUTOR/FX parsers
  }
  delay(10);
}