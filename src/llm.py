# src/llm.py
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = (
    "You are an encouraging habit coach. Be positive, specific, and actionable. "
    "When asked about meals, provide short feedback on portion control, meal balance, and a motivational closing sentence."
)

def chat_with_coach(messages, model: str = "gpt-4o-mini", temperature: float = 0.6):
    if not openai.api_key:
        return {"error": "No OPENAI_API_KEY set."}
    msgs = []
    msgs.append({"role": "system", "content": SYSTEM_PROMPT})
    msgs.extend(messages)
    resp = openai.ChatCompletion.create(model=model, messages=msgs, temperature=temperature, max_tokens=300)
    text = resp["choices"][0]["message"]["content"]
    return {"text": text, "raw": resp}
