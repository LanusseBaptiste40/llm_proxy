import requests
import os

API_KEY = os.getenv("LITELLM_MASTER_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

try:
    response = requests.get("http://localhost:4000/v1/models", headers=HEADERS, timeout=5)
    if response.status_code == 200:
        exit(0)
    else:
        exit(1)
except Exception:
    exit(1)