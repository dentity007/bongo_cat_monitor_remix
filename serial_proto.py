# serial_proto.py
import time, json, threading
from typing import Optional, Dict, Any, Tuple

import serial  # pyserial

PROTOCOL_MAJ = 2
PROTOCOL_MIN = 0
APP_NAME = "bongo_cat_app"
HELLO_TIMEOUT_S = 0.8
READ_TIMEOUT_S = 0.25

class ProtoError(Exception): pass
class VersionIncompatible(ProtoError): pass

def _parse_line(line: str) -> Tuple[str, Dict[str, str], Optional[Dict[str, Any]]]:
    line = line.strip()
    if not line:
        return "", {}, None
    parts = line.split(" ", 2)
    cmd = parts[0].upper()
    kv: Dict[str, str] = {}
    payload = None
    if len(parts) >= 2:
        # parse KEY=VALUE tokens
        rest = parts[1] if len(parts) == 2 else parts[1] + " " + parts[2]
        tokens = rest.split()
        for t in tokens:
            if "=" in t:
                k, v = t.split("=", 1)
                k_upper = k.upper()
                # Check if value is JSON
                if v.startswith("{") or v.startswith("["):
                    try:
                        payload = json.loads(v)
                        # Don't add JSON keys to kv dict
                    except json.JSONDecodeError:
                        kv[k_upper] = v
                else:
                    kv[k_upper] = v
            else:
                # support forms like CAP 0x1234
                if t.startswith("0x"):
                    kv.setdefault("VAL", t)
                else:
                    kv.setdefault("ARG", t)
    return cmd, kv, payload

def _send(ser: serial.Serial, line: str):
    ser.write((line.strip() + "\n").encode("utf-8"))

def hello(ser: serial.Serial, req_cap: int = 0xFFFFFFFF) -> Dict[str, Any]:
    """Perform version negotiation. Returns fw_info dict. Safe-degrades to legacy."""
    ser.timeout = READ_TIMEOUT_S
    msg = f'HELLO V={PROTOCOL_MAJ}.{PROTOCOL_MIN} REQCAP=0x{req_cap:08X} NAME="{APP_NAME}"'
    _send(ser, msg)

    deadline = time.time() + HELLO_TIMEOUT_S
    last = ""
    while time.time() < deadline:
        raw = ser.readline().decode("utf-8", errors="ignore")
        if not raw:
            continue
        last = raw
        cmd, kv, _ = _parse_line(raw)
        if cmd == "HELLO" and "V" in kv and "CAP" in kv:
            fw_ver = kv["V"]
            fw_major, fw_minor = [int(x) for x in fw_ver.split(".")]
            # major mismatch handling
            if fw_major != PROTOCOL_MAJ:
                raise VersionIncompatible(f"App v{PROTOCOL_MAJ}.{PROTOCOL_MIN} vs FW v{fw_ver}")
            return {
                "fw_ver": fw_ver,
                "cap": int(kv["CAP"], 16) if kv["CAP"].startswith("0x") else int(kv["CAP"]),
                "name": kv.get("NAME", "esp32").strip('"'),
                "fw": kv.get("FW", "")
            }
        # Some firmwares might respond with bare "CAP ..." first
        if cmd == "CAP" and ("VAL" in kv or "ARG" in kv):
            cap = kv.get("VAL") or kv.get("ARG")
            return {"fw_ver": "1.0-legacy", "cap": int(cap, 16) if cap.startswith("0x") else int(cap), "name": "esp32", "fw": ""}
    # No v2 HELLO; assume legacy firmware
    return {"fw_ver": "1.0-legacy", "cap": 0, "name": "esp32", "fw": ""}

def ping(ser: serial.Serial) -> bool:
    _send(ser, f"PING TS={int(time.time())}")
    raw = ser.readline().decode("utf-8", errors="ignore")
    cmd, kv, _ = _parse_line(raw)
    return cmd == "PONG"

def set_mode(ser: serial.Serial, mode: str) -> bool:
    _send(ser, f"SET MODE={mode}")
    raw = ser.readline().decode("utf-8", errors="ignore")
    cmd, kv, _ = _parse_line(raw)
    return cmd == "ACK" or raw.strip().upper().startswith("OK")

def trigger(ser: serial.Serial, name: str) -> bool:
    _send(ser, f"TRIGGER NAME={name}")
    raw = ser.readline().decode("utf-8", errors="ignore")
    cmd, kv, _ = _parse_line(raw)
    return cmd == "ACK" or raw.strip().upper().startswith("OK")

def send_temps(ser: serial.Serial, cpu: float = None, gpu: float = None):
    # Send only if app wants overlay support; firmware may NACK if unsupported
    payload = {}
    if cpu is not None: payload["cpu"] = cpu
    if gpu is not None: payload["gpu"] = gpu
    _send(ser, "DATA TEMPS=" + json.dumps(payload))