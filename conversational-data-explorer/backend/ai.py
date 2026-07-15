"""
ai.py
One tiny abstraction around the model call, so the rest of the app never
talks to the Gemini API directly. Swapping providers later means editing
only this file.
"""

import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class AIError(Exception):
    pass


def call_model(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    """
    Send a system + user prompt to Gemini and return the raw text response.
    Kept deliberately dumb: no parsing, no retries beyond one, no state.
    Callers (nl2sql.py) are responsible for interpreting the text.
    """
    if not GEMINI_API_KEY:
        raise AIError(
            "GEMINI_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": temperature},
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise AIError(f"Could not reach the model API: {e}") from e

    data = resp.json()
    try:
        candidates = data["candidates"]
        parts = candidates[0]["content"]["parts"]
        text_out = "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError) as e:
        raise AIError(f"Unexpected response shape from model API: {data}") from e

    if not text_out.strip():
        raise AIError("Model returned an empty response.")

    return text_out.strip()
