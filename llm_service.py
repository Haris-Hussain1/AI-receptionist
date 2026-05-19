import requests
from backend.config import config

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a professional AI receptionist named 3novatorTech Assistant. "
    "Keep all replies concise, formal, and courteous. Do not use emojis. "
    "If someone wants to book an appointment, let them know you can assist them with that."
)


def ask_llm(user_message: str) -> str:
    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 256,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
