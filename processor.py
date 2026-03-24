import requests
from config import OPENROUTER_BASE_URL, ProcessMode
from config import SUMMARY_PROMPT, CUSTOM_PROMPT_TEMPLATE

class AIProcessor:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://web-summary.local",
            "X-Title": "Web Summary"
        }

    def process(self, content: str, mode: ProcessMode, custom_prompt: str = None) -> str:
        """Process content with AI"""
        if mode == ProcessMode.SUMMARY:
            prompt = SUMMARY_PROMPT.format(content=content)
        else:
            prompt = CUSTOM_PROMPT_TEMPLATE.format(
                custom_prompt=custom_prompt or "analyze this content",
                content=content
            )
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]

    def validate_api(self) -> bool:
        """Validate API key"""
        response = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers=self.headers,
            timeout=10
        )
        return response.status_code == 200
