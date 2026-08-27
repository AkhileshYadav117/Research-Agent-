import os
import json
import time
import hashlib

CACHE_DIR = "groq_cache"
CACHE_TTL_SECONDS = 60 * 60 * 6  # 6 hours — good for active dev/testing

def _key(prompt: str) -> str:
    return hashlib.md5(prompt.strip().encode()).hexdigest()

def get_cached_response(prompt: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{_key(prompt)}.json")

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("timestamp", 0) > CACHE_TTL_SECONDS:
            return None
        cached_value = data.get("response")
        if not cached_value or not cached_value.strip():
            return None  # ignore corrupted/empty cache entries
        return cached_value
    except Exception:
        return None

def set_cached_response(prompt: str, response: str):
    if not response or not response.strip():
        return  # never cache empty/failed responses

    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{_key(prompt)}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "response": response}, f)
    except Exception:
        pass