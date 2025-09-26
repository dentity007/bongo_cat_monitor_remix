#include "protocol.h"

static bool startsWith(const String& s, const char* pfx) {
  return s.startsWith(pfx);
}

static String getToken(const String& s, const String& key) {
  // finds KEY=VALUE tokens; very simple parser
  int pos = s.indexOf(key + "=");
  if (pos < 0) return "";
  int start = pos + key.length() + 1;
  int end = s.indexOf(' ', start);
  if (end < 0) end = s.length();
  return s.substring(start, end);
}

static void sendHello(const ProtoInfo& info) {
  Serial.printf("HELLO V=%d.%d CAP=0x%08X NAME=\"%s\" FW=%s\n",
    info.major, info.minor, info.cap, info.name, info.fw);
}

static void sendAck(const char* cmd) {
  Serial.printf("ACK CMD=%s\n", cmd);
}

static void sendNack(const char* cmd, ErrCode e, const char* msg) {
  Serial.printf("NACK CMD=%s ERR=%d MSG=\"%s\"\n", cmd, (int)e, msg);
}

void handleLine(const String& line, const ProtoInfo& info) {
  String up = line; up.toUpperCase();

  if (startsWith(up, "HELLO")) {
    // App wants v2 negotiation
    sendHello(info);
    return;
  }

  if (startsWith(up, "PING")) {
    String ts = getToken(line, "TS");
    Serial.printf("PONG TS=%s\n", ts.length()? ts.c_str() : "0");
    return;
  }

  if (startsWith(up, "GET CAP")) {
    Serial.printf("CAP 0x%08X\n", info.cap);
    return;
  }

  if (startsWith(up, "SET MODE=")) {
    String mode = getToken(line, "MODE");
    // TODO: validate mode and switch
    // if unsupported:
    // sendNack("SET", MODE_UNSUPPORTED, "mode");
    sendAck("SET");
    return;
  }

  if (startsWith(up, "TRIGGER")) {
    String name = getToken(line, "NAME");
    // TODO: dispatch trigger "name"
    // if unknown: sendNack("TRIGGER", TRIGGER_UNKNOWN, "id");
    sendAck("TRIGGER");
    return;
  }

  if (startsWith(up, "DATA TEMPS=")) {
    // Optional: parse small JSON or just ignore for now
    sendAck("DATA");
    return;
  }

  // Legacy simple forms (unversioned), kept for fallback
  if (startsWith(up, "MODE ")) {
    // MODE <name>
    sendAck("SET");
    return;
  }
  if (startsWith(up, "TRIGGER ")) {
    sendAck("TRIGGER");
    return;
  }

  sendNack("?", UNKNOWN_CMD, "unknown");
}