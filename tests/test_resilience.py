import time
from resilience import TTLCache, CircuitBreaker

def test_ttlcache_hit_and_stale():
    c = TTLCache()
    c.put("k", 123)
    hit, val, stale = c.get("k", ttl_s=1)
    assert hit and val == 123 and not stale
    time.sleep(1.1)
    hit, val, stale = c.get("k", ttl_s=1)
    assert hit and stale

def test_circuit_breaker_transitions(tmp_path, monkeypatch):
    # Isolated state file
    monkeypatch.setattr("resilience.CB_STATE_PATH", str(tmp_path/"cb.json"))
    b = CircuitBreaker("unit", fail_threshold=2, open_window_s=1)
    assert b.allow()
    b.record_failure()
    assert b.state == "CLOSED"
    b.record_failure()
    assert b.state == "OPEN"
    assert not b.allow()
    time.sleep(1.1)
    assert b.allow()  # HALF_OPEN probe
    b.record_success()
    assert b.state == "CLOSED"