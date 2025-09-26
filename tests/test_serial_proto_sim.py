import io
from serial_proto import _parse_line

def test_parse_line_examples():
    cmd, kv, _ = _parse_line('HELLO V=2.0 CAP=0x00000037 NAME="esp32" FW=2025.09.26')
    assert cmd == "HELLO"
    assert kv["V"] == "2.0"
    assert kv["CAP"] == "0x00000037"

    cmd, kv, _ = _parse_line('CAP 0x00000037')
    assert cmd == "CAP"
    assert kv["VAL"] == "0x00000037"

def test_payload_json():
    cmd, kv, payload = _parse_line('DATA TEMPS={"cpu":42.5,"gpu":55.0}')
    assert cmd == "DATA"
    assert "TEMPS" not in kv
    assert payload["cpu"] == 42.5