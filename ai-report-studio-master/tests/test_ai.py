import pytest

import ai
from ai import generate_report


@pytest.fixture(autouse=True)
def _reset_model(monkeypatch):
    # Reset the cached model before the test to prevent stale leakage.
    ai.reset_ai_model()
    # Use monkeypatch so the env var is automatically restored after the test.
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-tests")
    yield
    # Reset again after the test (existing behavior).
    ai.reset_ai_model()


def test_generate_report_success(monkeypatch):
    fake_response = type("R", (), {"text": "Generated"})()
    fake_model = type("M", (), {"generate_content": lambda self, p: fake_response})()
    fake_ctor = lambda name: fake_model

    monkeypatch.setattr(ai.genai, "GenerativeModel", fake_ctor)

    result = generate_report("prompt")
    assert result == "Generated"


def test_generate_report_error(monkeypatch):
    def _boom(self, prompt):
        raise Exception("API Error")

    fake_model = type("M", (), {"generate_content": _boom})()
    fake_ctor = lambda name: fake_model

    monkeypatch.setattr(ai.genai, "GenerativeModel", fake_ctor)

    with pytest.raises(Exception) as exc_info:
        generate_report("prompt")

    assert "Failed to generate report" in str(exc_info.value)
