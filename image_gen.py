import requests
from urllib.parse import quote

def generate_image(prompt: str) -> bytes:
    """
    Generates an image using Pollinations.ai (free, no API key required).
    Returns image bytes, or empty bytes if it fails.
    """
    try:
        # Clean the prompt: strip common trigger phrases so only the
        # actual subject description is sent to the image model
        clean_prompt = prompt.lower()
        for trigger in [
            "generate an image of", "generate image of", "create an image of",
            "create image of", "make an image of", "make image of",
            "draw", "generate a picture of", "create a picture of",
            "show me a picture of", "picture of", "image of",
            "generate art of", "create art of", "paint", "illustrate",
        ]:
            clean_prompt = clean_prompt.replace(trigger, "")
        clean_prompt = clean_prompt.strip(" :.,") or prompt

        encoded_prompt = quote(clean_prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=1024&nologo=true&model=flux&enhance=true"
        )

        response = requests.get(url, timeout=45)
        response.raise_for_status()
        return response.content
    except Exception:
        return b""

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
    query_lower = query.lower()
    return any(trigger in query_lower for trigger in triggers)