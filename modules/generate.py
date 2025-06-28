# modules/generate.py

import requests

LM_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_ID = "mythomax-l2-13b"  # Confirmed from your curl

def query_llm(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lm-studio"  # Required by LM Studio API
    }

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": "You are Jarvis, Ryan's personal AI assistant. Speak clearly, concisely, and helpfully."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(LM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Jarvis Error] LLM failed: {e}")
        return "Sorry, I'm having trouble accessing the local model right now."
