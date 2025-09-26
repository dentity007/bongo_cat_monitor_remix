# resilience.py
import json, os, time, threading, random, logging
from typing import Any, Dict, Optional, Tuple, Callable

try:
    import requests
except Exception:
    requests = None  # caller should guard or add requests to deps

log = logging.getLogger("resilience")

# -------- Simple disk paths (adjust if you want a dedicated app dir) --------
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
DISK_CACHE_PATH = os.path.join(CACHE_DIR, "api_cache.json")
CB_STATE_PATH   = os.path.join(CACHE_DIR, "cb_state.json")

# -------------------- Telemetry (very lightweight) --------------------------
class Telemetry:
    def __init__(self):
        self.counters = {
            "cache_hits": 0,
            "cache_stale_hits": 0,
            "cache_misses": 0,
            "fetch_success": 0,
            "fetch_fail": 0,
            "cb_open": 0,
            "cb_half_open": 0,
            "cb_close": 0,
        }

    def inc(self, key: str, n: int = 1):
        self.counters[key] = self.counters.get(key, 0) + n

    def snapshot(self) -> Dict[str, int]:
        return dict(self.counters)

TELEMETRY = Telemetry()

# ------------------------ In-memory TTL cache -------------------------------
class TTLCache:
    def __init__(self):
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str, ttl_s: int) -> Tuple[bool, Optional[Any], bool]:
        """
        returns (hit, value, is_stale)
        - hit = True if we have any value
        - is_stale = True if present but expired
        """
        now = time.time()
        if key in self._store:
            t, val = self._store[key]
            is_stale = (now - t) > ttl_s
            if is_stale:
                return True, val, True
            return True, val, False
        return False, None, False

    def put(self, key: str, val: Any):
        self._store[key] = (time.time(), val)

MEM_CACHE = TTLCache()

# ----------------------- Disk cache (optional) ------------------------------
def _read_disk_cache() -> Dict[str, Any]:
    if not os.path.exists(DISK_CACHE_PATH):
        return {}
    try:
        with open(DISK_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_disk_cache(obj: Dict[str, Any]):
    try:
        with open(DISK_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
    except Exception:
        pass

# ----------------------- Circuit Breaker ------------------------------------
class CircuitBreaker:
    """
    States:
      - CLOSED: allow calls. After N consecutive failures -> OPEN
      - OPEN: block calls for open_window_s, immediately use fallback
      - HALF_OPEN: after open window, allow 1 trial. Success -> CLOSED (reset)
                   failure -> OPEN again
    """
    def __init__(self, name: str, fail_threshold: int = 3, open_window_s: int = 600):
        self.name = name
        self.fail_threshold = fail_threshold
        self.open_window_s = open_window_s
        self.state = "CLOSED"
        self.fail_count = 0
        self.open_since = 0.0
        self._load()

    def _load(self):
        try:
            with open(CB_STATE_PATH, "r", encoding="utf-8") as f:
                all_state = json.load(f)
            s = all_state.get(self.name)
            if s:
                self.state = s["state"]
                self.fail_count = s["fail_count"]
                self.open_since = s["open_since"]
        except Exception:
            pass

    def _save(self):
        try:
            all_state = {}
            if os.path.exists(CB_STATE_PATH):
                with open(CB_STATE_PATH, "r", encoding="utf-8") as f:
                    all_state = json.load(f)
            all_state[self.name] = {
                "state": self.state,
                "fail_count": self.fail_count,
                "open_since": self.open_since,
            }
            with open(CB_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(all_state, f, indent=2)
        except Exception:
            pass

    def allow(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            if (now - self.open_since) >= self.open_window_s:
                self.state = "HALF_OPEN"
                TELEMETRY.inc("cb_half_open")
                self._save()
                return True  # allow a probe call
            return False
        return True  # CLOSED or HALF_OPEN

    def record_success(self):
        self.fail_count = 0
        if self.state in ("OPEN", "HALF_OPEN"):
            self.state = "CLOSED"
            TELEMETRY.inc("cb_close")
        self._save()

    def record_failure(self):
        self.fail_count += 1
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.open_since = time.time()
            TELEMETRY.inc("cb_open")
        elif self.fail_count >= self.fail_threshold:
            self.state = "OPEN"
            self.open_since = time.time()
            TELEMETRY.inc("cb_open")
        self._save()

# ----------------------- Fetch with retries ---------------------------------
def fetch_json_with_retries(url: str, timeout_s: float = 1.5,
                            attempts: int = 3, base_delay_s: float = 0.25,
                            max_delay_s: float = 2.0) -> Any:
    if not requests:
        raise RuntimeError("requests not installed")
    last_exc = None
    for i in range(attempts):
        try:
            r = requests.get(url, timeout=timeout_s)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_exc = e
            # exponential backoff with jitter
            delay = min(max_delay_s, base_delay_s * (2 ** i)) + random.uniform(0, 0.1)
            time.sleep(delay)
    raise last_exc

# ------------------------ Public helper: resilient JSON ---------------------
def resilient_json(
    name: str,
    url: str,
    cache_key: str,
    ttl_s: int,
    local_fallback_fn: Callable[[], Any],
    non_blocking: bool = True,
) -> Tuple[Any, Dict[str, Any]]:
    """
    Returns (data, meta)
      - Never raises to caller
      - Uses in-memory and disk cache
      - Uses circuit breaker
      - Optionally returns immediately with cached/stale (non_blocking=True) and refreshes in background
    meta: {source: "mem|disk|network|stale|fallback", telemetry: {...}, breaker_state: "..."}
    """
    breaker = CircuitBreaker(name)
    meta: Dict[str, Any] = {"source": None, "breaker_state": breaker.state}

    # 1) Memory cache
    hit, val, stale = MEM_CACHE.get(cache_key, ttl_s)
    if hit and not stale:
        TELEMETRY.inc("cache_hits")
        meta["source"] = "mem"
        meta["telemetry"] = TELEMETRY.snapshot()
        meta["breaker_state"] = breaker.state
        return val, meta

    # 2) Disk cache (used if mem miss or stale)
    disk = _read_disk_cache()
    if cache_key in disk:
        entry = disk[cache_key]
        age = time.time() - entry.get("ts", 0)
        if age <= ttl_s:
            MEM_CACHE.put(cache_key, entry["data"])
            TELEMETRY.inc("cache_hits")
            meta["source"] = "disk"
            meta["telemetry"] = TELEMETRY.snapshot()
            meta["breaker_state"] = breaker.state
            return entry["data"], meta
        else:
            TELEMETRY.inc("cache_stale_hits")

    # Helper to persist a fresh value
    def _persist(val_any: Any):
        MEM_CACHE.put(cache_key, val_any)
        disk = _read_disk_cache()
        disk[cache_key] = {"ts": time.time(), "data": val_any}
        _write_disk_cache(disk)

    # 3) If we have stale value and we're in non_blocking mode: return stale now, refresh in bg
    if hit and stale and non_blocking:
        stale_val = val
        meta["source"] = "stale"
        meta["telemetry"] = TELEMETRY.snapshot()
        meta["breaker_state"] = breaker.state

        def _bg_refresh():
            if not breaker.allow():
                return
            try:
                data = fetch_json_with_retries(url)
                _persist(data)
                TELEMETRY.inc("fetch_success")
                breaker.record_success()
            except Exception:
                TELEMETRY.inc("fetch_fail")
                breaker.record_failure()
        threading.Thread(target=_bg_refresh, daemon=True).start()
        return stale_val, meta

    # 4) Try network if breaker allows
    if breaker.allow():
        try:
            data = fetch_json_with_retries(url)
            _persist(data)
            TELEMETRY.inc("fetch_success")
            breaker.record_success()
            meta["source"] = "network"
            meta["telemetry"] = TELEMETRY.snapshot()
            meta["breaker_state"] = breaker.state
            return data, meta
        except Exception:
            TELEMETRY.inc("fetch_fail")
            breaker.record_failure()

    # 5) Fallback to local/static
    fb = local_fallback_fn()
    meta["source"] = "fallback"
    meta["telemetry"] = TELEMETRY.snapshot()
    meta["breaker_state"] = breaker.state
    return fb, meta