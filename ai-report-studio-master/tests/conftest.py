import unittest.mock as mock

import pytest


@pytest.fixture(autouse=True)
def disable_real_ai_calls():
    """Force the /reports endpoint to use its template fallback in tests.

    Prevents any test from hitting the real Gemini API (slow, costly, flaky),
    regardless of whether GEMINI_API_KEY is set in the environment. Tests that
    want to exercise the AI-success path override this with their own
    mock.patch('main.ai_generate_report', ...) context manager.
    """
    with mock.patch(
        "main.ai_generate_report", side_effect=Exception("AI disabled in tests")
    ):
        yield
