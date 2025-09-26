#pragma once
#include <Arduino.h>

struct ProtoInfo {
  uint8_t major = 2;
  uint8_t minor = 0;
  uint32_t cap  = 0x00000037; // adjust to your device
  const char* name = "esp32";
  const char* fw   = "2025.09.26";
};

enum ErrCode : int {
  UNKNOWN_CMD=1, BAD_ARGS=2, MODE_UNSUPPORTED=3, TRIGGER_UNKNOWN=4, BUSY=5, INTERNAL=6
};

class LineReader {
 public:
  explicit LineReader(Stream& s): io(s) {}
  bool readLine(String& out) {
    while (io.available()) {
      char c = (char)io.read();
      if (c == '\r') continue;
      if (c == '\n') { out = buf; buf = ""; return true; }
      buf += c;
      if (buf.length() > 240) buf.remove(0, buf.length()-240);
    }
    return false;
  }
 private:
  Stream& io;
  String buf;
};