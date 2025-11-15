import requests
import base64
import os

HF_TOKEN = "your_finegrained_token"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

payload = {
    "model": "stabilityai/stable-diffusion-xl-base-1.0",
    "prompt": "technical blueprint lineart of disc brake front view",
    "width": 768,
    "height": 768
}

resp = requests.post(
    "https://router.huggingface.co/sdapi/v1/txt2img",
    headers=headers,
    json=payload
)

print(resp.status_code)
print(resp.text[:500])
