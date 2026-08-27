import os
import time
import requests
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Prompt cleaner — strips trigger phrases so only the subject is sent
# ---------------------------------------------------------------------------
_TRIGGERS = [
    "generate an image of", "generate image of", "create an image of",
    "create image of", "make an image of", "make image of",
    "draw a", "draw an", "draw", "generate a picture of", "create a picture of",
    "show me a picture of", "picture of", "image of",
    "generate art of", "create art of", "paint", "illustrate",
    "generate an", "generate a", "create an", "create a",
    "make a", "make an",
]

def _clean_prompt(prompt: str) -> str:
    cleaned = prompt.lower()
    for t in _TRIGGERS:
        cleaned = cleaned.replace(t, "")
    cleaned = cleaned.strip(" :.,!?") or prompt
    # Add quality boosters for better results
    return cleaned + ", high quality, detailed, photorealistic, 4k"


# ---------------------------------------------------------------------------
# Primary: Hugging Face Inference API — FLUX.1-schnell (FREE)
# ---------------------------------------------------------------------------
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
HF_MODEL   = "black-forest-labs/FLUX.1-schnell"
HF_URL     = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def _generate_via_huggingface(prompt: str) -> bytes:
    if not HF_API_KEY:
        return b""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,   # schnell is optimized for 4 steps
            "guidance_scale": 0.0,      # schnell works best at 0 guidance
        }
    }
    # Retry up to 3 times (model may be loading on first call)
    for attempt in range(3):
        try:
            resp = requests.post(HF_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200 and resp.content:
                return resp.content
            if resp.status_code == 503:
                # Model is loading — wait and retry
                time.sleep(10)
                continue
        except Exception:
            time.sleep(3)
    return b""


# ---------------------------------------------------------------------------
# Fallback: Pollinations.ai (no API key needed, free)
# ---------------------------------------------------------------------------
def _generate_via_pollinations(prompt: str) -> bytes:
    try:
        encoded = quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1024&nologo=true&model=flux&enhance=true&seed={int(time.time())}"
        )
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        if len(resp.content) > 5000:   # valid image is always > 5KB
            return resp.content
    except Exception:
        pass
    return b""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_image(prompt: str) -> bytes:
    """
    Generates an image from a text prompt.
    1st: Hugging Face FLUX.1-schnell (high quality, free with API key)
    2nd: Pollinations.ai (fallback, no key needed)
    Returns image bytes, or empty bytes if both fail.
    """
    clean = _clean_prompt(prompt)

    # Try HuggingFace first if key is set
    if HF_API_KEY:
        result = _generate_via_huggingface(clean)
        if result:
            return result

    # Fallback to Pollinations
    return _generate_via_pollinations(clean)


def is_image_request(query: str) -> bool:
    """
    Detects if the query is asking for image generation rather than research.
    """
    triggers = [
        "generate an image", "generate image", "create an image", "create image",
        "draw", "make an image", "make image", "generate a picture",
        "create a picture", "show me a picture", "picture of", "image of",
        "generate art", "create art", "paint", "illustrate",
    ]
    return any(t in query.lower() for t in triggers)
