import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def reset_ai_model():
    """Reset the cached model singleton. Useful for tests and reconfiguration."""
    global _model
    _model = None


def get_ai_model():
    """Return a lazily-initialized singleton GenerativeModel.

    Reads GEMINI_API_KEY from the environment on first use (raises a clear
    ValueError if missing) and configures the SDK. The model is constructed
    only when first requested, never at import time.
    """
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Set it in your environment or .env file."
            )
        genai.configure(api_key=api_key)
        model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        _model = genai.GenerativeModel(model_name)
    return _model


def generate_report(prompt: str) -> str:
    """Generate a report from the given prompt using the configured model.

    Returns the generated text. Any failure is wrapped in an Exception whose
    message starts with "Failed to generate report: ".
    """
    try:
        model = get_ai_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        raise Exception(f"Failed to generate report: {exc}") from exc
