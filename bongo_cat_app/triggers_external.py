# triggers_external.py
from typing import Any, Dict, Tuple, List
from resilience import resilient_json

IMGFLIP_URL = "https://api.imgflip.com/get_memes"  # example endpoint
CACHE_KEY   = "imgflip_memes"
TTL_S       = 60 * 60 * 24  # 1 day

def _local_fallback() -> Dict[str, Any]:
    # Return your built-in, offline/static trigger list
    # Minimal shape compatible with your code:
    return {"success": True, "data": {"memes": [
        {"id": "local_1", "name": "Local Drake", "url": "assets/triggers/drake.png"},
        {"id": "local_2", "name": "Local Epic",  "url": "assets/triggers/epic.png"},
    ]}}

def get_memes(non_blocking: bool = True) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Returns (data, meta). meta['source'] in {'mem','disk','network','stale','fallback'}
    """
    return resilient_json(
        name="imgflip_templates",
        url=IMGFLIP_URL,
        cache_key=CACHE_KEY,
        ttl_s=TTL_S,
        local_fallback_fn=_local_fallback,
        non_blocking=non_blocking,
    )

def extract_template_names(resp: Dict[str, Any]) -> List[str]:
    # helper you can use in UI/logs
    try:
        return [m["name"] for m in resp["data"]["memes"]]
    except Exception:
        return []