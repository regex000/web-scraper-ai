import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://web-summary.local",
    "X-Title": "Web Summary"
}

payload = {
    "model": "nvidia/nemotron-3-super",
    "messages": [{"role": "user", "content": "Hello, test"}],
    "temperature": 0.7,
    "max_tokens": 100
}

response = requests.post(
    f"{OPENROUTER_BASE_URL}/chat/completions",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
