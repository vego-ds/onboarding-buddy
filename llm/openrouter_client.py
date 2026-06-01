import os
import requests
from dotenv import load_dotenv

load_dotenv()


def call_openrouter(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv(
        "OPENROUTER_MODEL",
        "meta-llama/llama-3.1-8b-instruct"
    )

    base_url = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1"
    )

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from .env")

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]
