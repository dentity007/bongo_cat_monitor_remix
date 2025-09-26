# Bongo Cat Serial Protocol v2

**Framing:** ASCII lines, LF `\n` terminated.  
**Shape:** `COMMAND [KEY=VALUE ...] [JSON]` (JSON last, optional).  
**Encoding:** UTF-8.

## Version negotiation
App sends:


HELLO V=2.0 REQCAP=0x000000FF NAME="bongo_cat_app"

Firmware replies:


HELLO V=2.0 CAP=0x00000037 NAME="esp32" FW=2025.09.26

- If **major mismatch**, app shows warning and uses legacy fallback if available.
- If **minor mismatch**, proceed and gate features via CAP.

**Timeouts:**
- App waits 800 ms for `HELLO` after sending its `HELLO` (retry x2).
- Firmware waits 1200 ms for `HELLO` after first byte; if none, stays in legacy mode.

## Capabilities
Bitmask (LSB first):
- 0x0001 DISPLAY_ILI9341
- 0x0002 DISPLAY_ST7789
- 0x0004 BUTTONS
- 0x0008 SERIAL_2M
- 0x0010 TEMP_OVERLAY
- 0x0020 MESSENGER_MODE
- 0x0040 TUTOR_MODE
- 0x0080 OTA_SUPPORTED

## Commands

App → Firmware
- `HELLO V=<maj.min> REQCAP=<hex> NAME="<str>"`
- `PING TS=<unix>`
- `GET CAP`
- `SET MODE=<normal|messenger|tutor>`
- `TRIGGER NAME=<id>`
- `DATA TEMPS={"cpu":<float>,"gpu":<float>}`

Firmware → App
- `HELLO V=<maj.min> CAP=<hex> NAME="<str>" FW=<yyyymmdd or semver>`
- `ACK CMD=<name>`
- `NACK CMD=<name> ERR=<code> MSG="<human>"`
- `CAP <hex>`
- `PONG TS=<unix>`
- `ERR ERR=<code> MSG="<human>"`
- `EVENT BTN={"a":0|1,"b":0|1}`

## Error codes
- `1` UNKNOWN_CMD
- `2` BAD_ARGS
- `3` MODE_UNSUPPORTED
- `4` TRIGGER_UNKNOWN
- `5` BUSY
- `6` INTERNAL

## Legacy fallback
If no `HELLO`, accept:
- `TRIGGER <id>`
- `MODE <name>`
Respond with simple `OK` or `ERR <msg>`.