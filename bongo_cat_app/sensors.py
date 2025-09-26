# sensors.py
from typing import Dict, Any, Optional

# Optional deps
try:
    import requests  # for LibreHardwareMonitor HTTP JSON endpoint
except Exception:
    requests = None

def is_admin_windows() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

# ----- Provider 1: LibreHardwareMonitor HTTP (no admin for THIS app) -----
# Ask users to run LibreHardwareMonitor and enable "Remote Web Server" (default http://localhost:8085)
def read_lhm_http(url: str = "http://localhost:8085/data.json") -> Dict[str, Any]:
    if not requests:
        raise RuntimeError("The 'requests' package is required for LibreHardwareMonitor HTTP provider.")
    r = requests.get(url, timeout=1.5)
    r.raise_for_status()
    return r.json()

def summarize_lhm(tree: Dict[str, Any]) -> Dict[str, Optional[float]]:
    temps: Dict[str, float] = {}

    def walk(node):
        text = node.get("Text", "")
        if "Temperature" in text and "Value" in node:
            label = text.split("Temperature")[0].strip() or "Temp"
            try:
                temps[label] = float(node["Value"])
            except Exception:
                pass
        for ch in node.get("Children", []):
            walk(ch)
    walk(tree)
    return {
        "cpu_temp_c": temps.get("CPU"),
        "gpu_temp_c": temps.get("GPU"),
        "_raw_count": len(temps)
    }

# ----- Provider 2: NVML (NVIDIA GPU only; user-level) -----
def read_nvml_gpu_temp() -> Optional[float]:
    try:
        import nvidia_smi
        nvidia_smi.nvmlInit()
        count = nvidia_smi.nvmlDeviceGetCount()
        if count < 1:
            nvidia_smi.nvmlShutdown()
            return None
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        temp = nvidia_smi.nvmlDeviceGetTemperature(handle, nvidia_smi.NVML_TEMPERATURE_GPU)
        nvidia_smi.nvmlShutdown()
        return float(temp)
    except Exception:
        return None

def read_sensors(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Least-privilege strategy:
      provider=auto (default): try LHM HTTP (no admin), else NVML GPU temp.
      provider=lhm_http: require LibreHardwareMonitor Remote Web Server enabled.
      provider=nvml: NVIDIA GPU only.
    """
    telemetry = cfg.get("telemetry", {})
    provider = telemetry.get("provider", "auto")
    gpu_only = telemetry.get("gpu_only", True)

    if provider in ("auto", "lhm_http"):
        try:
            data = read_lhm_http()
            summary = summarize_lhm(data)
            if gpu_only:
                return {"gpu_temp_c": summary.get("gpu_temp_c")}
            return summary
        except Exception:
            if provider == "lhm_http":
                raise

    if provider in ("auto", "nvml"):
        gpu = read_nvml_gpu_temp()
        if gpu is not None:
            return {"gpu_temp_c": gpu}

    return {"gpu_temp_c": None, "cpu_temp_c": None}