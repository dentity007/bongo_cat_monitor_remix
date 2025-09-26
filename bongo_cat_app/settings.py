# settings.py
import json, os
from typing import Dict, Any

DEFAULTS: Dict[str, Any] = {
    "telemetry": {
        "hardware_monitoring_enabled": False,   # master switch; opt-in
        "hardware_monitoring_consented": False, # one-time gate
        "provider": "auto",                     # auto | lhm_http | nvml
        "gpu_only": True                        # least-privilege default
    }
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

def load() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        save(DEFAULTS)
        return json.loads(json.dumps(DEFAULTS))  # deep copy
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # merge defaults for new keys
    def _merge(dst, src):
        for k, v in src.items():
            if isinstance(v, dict):
                dst[k] = _merge(dst.get(k, {}), v)
            else:
                dst.setdefault(k, v)
        return dst
    return _merge(data, json.loads(json.dumps(DEFAULTS)))

def save(cfg: Dict[str, Any]) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def is_monitoring_allowed(cfg: Dict[str, Any]) -> bool:
    t = cfg.get("telemetry", {})
    return bool(t.get("hardware_monitoring_enabled") and t.get("hardware_monitoring_consented"))